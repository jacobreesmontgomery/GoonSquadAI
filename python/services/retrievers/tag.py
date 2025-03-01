from sqlalchemy import text, Sequence, Row, Any
from tenacity import retry, stop_after_attempt, wait_random_exponential

from prompts.tag import tag_prompt
from models.activity import Activity
from models.athlete import Athlete
from database import DatabaseService
from services.openai import OpenAIService
from utils.simple_logger import SimpleLogger


class TAGRetriever:
    """
    Handles the TAG mechanism to retrieve athlete's training data.
    """

    def __init__(
        self,
        db_service: DatabaseService = DatabaseService(),
        openai_client: OpenAIService = OpenAIService(),
    ):
        """
        Initializes the TAG retriever.

        :param db_service: The database service.
        :param openai_client: The OpenAI service.

        :return: None
        """
        self.prompt: str = tag_prompt
        self.schema_description: str = self.establish_schema_description()
        self.db_service: DatabaseService = db_service
        self.openai_service: OpenAIService = openai_client
        self.error_msg: str = ""
        self.logger = SimpleLogger(log_level="INFO", class_name=__name__).logger

    def establish_schema_description(self) -> str:
        """
        Establishes the schema description for the TAG prompt.

        :return: The schema description.
        """
        activity_desc = Activity().convert_to_schema_description()
        athlete_desc = Athlete().convert_to_schema_description()
        schema_desc = f"{activity_desc}\n{athlete_desc}"
        return schema_desc

    def clean_query(query: str) -> str:
        """
        Cleans the LLM-generated SQL query by removing Markdown-style formatting.

        :param query: The generated SQL query.

        :return: The cleaned SQL query.
        """
        return (
            query.strip()  # Remove leading/trailing whitespace
            .replace("```sql", "")  # Remove opening Markdown SQL block
            .replace("```", "")  # Remove closing Markdown block
            .strip()  # Trim any remaining spaces
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(min=1, max=10),
    )
    def execute_query(
        self,
        user_question: str,
        schema_desc: str = None,
        gpt_model: str = None,
    ) -> tuple[Sequence[Row[Any]], int, int]:
        """
        Executes the generated SQL query and returns the results.

        :param user_question: The user's question.
        :param schema_desc: The schema description for the database.
        :param gpt_model: The GPT model to use for generating the query (e.g., "gpt-4o-mini").

        :return: The query results, the number of results, and the completion ID.
        """

        if not schema_desc:
            schema_desc = self.schema_description

        # Generate a query based on the user's question
        messages: list[dict[str, str]] = []
        if self.error_msg:
            messages.append({"role": "developer", "content": self.error_msg})

        messages.append(
            {
                "role": "user",
                "content": f"{tag_prompt.format(schema_description=schema_desc, user_question=user_question)}",
            }
        )

        self.logger.debug(f"Messages being fed in to the LLM:\n{messages}")
        query_result = self.openai_service.process_request(
            model=gpt_model if gpt_model else self.openai_service.model,
            messages=messages,
        )
        completion_id = query_result.id
        self.logger.debug(f"Chat completed: {completion_id}")

        # Clean up the query so it's executable
        query = query_result.choices[0].message.content
        query_to_execute = self.clean_query(query)

        # Execute the query
        session = self.db_service.get_session()
        try:
            self.logger.debug(f"\nExecuting this generated query: {query_to_execute}")
            result = session.execute(text(query_to_execute)).fetchall()
        except Exception as e:
            self.error_msg = f"An error occurred while executing this query: {query_to_execute}.\nHere is the error: {e}\nPlease generate a query to resolve this issue.\n"
            self.logger.error(self.error_msg)
            self.db_service.close_session()  # Close session before retry
            raise e  # Hit the retry mechanism
        self.db_service.close_session()

        return result, len(result), completion_id

    def process_tag_query(self, user_question: str, gpt_model: str = None) -> str:
        """
        Processes the TAG query and returns the results.

        :param user_question: The user's question.
        :param gpt_model: The GPT model to use for generating the query (e.g., "gpt-4o-mini").

        :return: The query results, the number of results, and the completion ID.
        """

        result, num_rows, completion_id = self.execute_query(
            user_question=user_question
        )

        # Display the results
        formatted_result = "\n".join([str(row) for row in result])
        self.logger.debug(
            f"\nQuery executed successfully. Number of rows returned: {num_rows}"
        )
        self.logger.debug(f"\nQuery Result:\n{formatted_result}")

        # Return an answer to the user
        messages = self.openai_service.get_past_messages(completion_id=completion_id)
        messages.append(
            {
                "role": "developer",
                "content": f"""
                    The user previously asked a question, and a SQL query was executed to retrieve relevant data.
                    The query result is:

                    {formatted_result}

                    Your task is to **write a natural language answer** to the user.
                    Do **NOT** generate another SQL query. Simply provide a clear, well-written summary response.

                    Additionally, if it makes sense, use a Markdown-formatted table to hold the data.
                """,
            }
        )
        ai_response = (
            self.openai_service.process_request(
                messages=messages,
                model=gpt_model if gpt_model else self.openai_service.model,
            )
            .choices[0]
            .message.content
        )
        self.logger.debug(f"\n{ai_response}")

        return ai_response
