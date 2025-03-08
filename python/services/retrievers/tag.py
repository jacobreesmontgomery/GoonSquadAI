from sqlalchemy import text, Sequence, Row, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
from json import loads

from prompts.tag import tag_prompt
from models.activity import Activity
from models.athlete import Athlete
from models.chat import (
    ChatResponse,
    ChatResponseMeta,
    OpenAIMessage,
    RoleTypes,
    GeneratedQueryOutput,
)
from models.base import APIResponsePayload
from models.exceptions import (
    LowConfidenceQueryException,
    QueryExecutionException,
    QueryGenerationException,
)
from services.database import DatabaseService
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

    def clean_query(self, query: str) -> str:
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
        retry=retry_if_exception_type(
            [QueryGenerationException, QueryExecutionException]
        ),
    )
    def execute_query(
        self,
        user_question: dict[str, str],
        messages: list[dict[str, str]],
        schema_desc: str = None,
        gpt_model: str = None,
    ) -> tuple[Sequence[Row[Any]], int, int, str] | str:
        """
        Executes the generated SQL query and returns the results.

        :param user_question: The user's question.
        :param messages: The list of messages.
        :param schema_desc: The schema description for the database.
        :param gpt_model: The GPT model to use for generating the query (e.g., "gpt-4o-mini").

        :return: The query results, the number of results, the completion ID, and the query to execute,
                    OR follow-up questions to ask the user.
        """

        if not schema_desc:
            schema_desc = self.schema_description

        # Generate a query based on the user's question
        if self.error_msg:
            messages.append({"role": RoleTypes.DEVELOPER, "content": self.error_msg})

        # NOTE - Consideration: Only append the full TAG prompt if it's not already in the messages
        messages.append(
            {
                "role": RoleTypes.DEVELOPER,
                "content": tag_prompt.format(
                    schema_description=schema_desc,
                    conversation=messages,
                    user_question=user_question,
                ),
            }
        )

        self.logger.debug(f"Messages being fed in to the LLM:\n{messages}")
        query_result = self.openai_service.process_request(
            messages=messages,
            model=gpt_model if gpt_model else self.openai_service.model,
        )
        completion_id = query_result.id
        self.logger.debug(f"Chat completed: {completion_id}")

        # Clean things up and get an executable query
        try:
            # Replace single quotes with double quotes for the JSON object
            query_result.choices[0].message.content = (
                query_result.choices[0]
                .message.content.replace("```", "")
                .replace("json", "")
            )
            json_result_data = loads(query_result.choices[0].message.content)
            json_result: GeneratedQueryOutput = GeneratedQueryOutput.parse_obj(
                json_result_data
            )
            follow_ups = json_result.follow_ups if json_result.follow_ups else None
            confidence = json_result.confidence
            if confidence == "LOW":
                if not follow_ups:
                    follow_ups = "Could you please elaborate on your question?"
                self.error_msg = f"Confidence level is {confidence}. Follow-up questions: {follow_ups}."
                self.logger.error(self.error_msg)
                return follow_ups
            query_to_execute = self.clean_query(json_result.query)
        except Exception as e:
            self.error_msg = f"An error occurred during query generation: {query_result.choices[0].message.content}. Here is the error: {e}\nPlease try again.\n"
            self.logger.error(self.error_msg)
            raise QueryGenerationException(
                message=self.error_msg
            )  # Hit the retry mechanism

        # Execute the query
        session = self.db_service.get_session()
        try:
            self.logger.debug(f"\nExecuting this generated query: {query_to_execute}")
            result = session.execute(text(query_to_execute)).fetchall()
        except Exception as e:
            self.error_msg = f"An error occurred while executing this query: {query_to_execute}.\nHere is the error: {e}\nPlease generate a query to resolve this issue.\n"
            self.logger.error(self.error_msg)
            self.db_service.close_session()  # Close session before retry
            raise QueryExecutionException(
                message=self.error_msg
            )  # Hit the retry mechanism
        self.db_service.close_session()

        return result, len(result), completion_id, query_to_execute

    def process(
        self,
        user_question: dict[str, str],
        messages: list[dict[str, str]],
        gpt_model: str = None,
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Processes the TAG query and returns the AI response.

        :param user_question: The user's most recent question.
        :param messages: The list of messages.
        :param gpt_model: The GPT model to use for generating the query (e.g., "gpt-4o-mini").

        :return The response payload.
        """

        result = self.execute_query(user_question=user_question, messages=messages)

        if isinstance(result, str):
            # The LLM had low confidence and provided follow-up questions
            return APIResponsePayload(
                data=ChatResponse(
                    response=OpenAIMessage(role=RoleTypes.ASSISTANT, content=result)
                ),
                meta=ChatResponseMeta(
                    completion_id=None,
                    executed_query=None,
                ),
            )

        # Unpack the tuple result
        result, num_rows, completion_id, executed_query = result

        # Display the results
        formatted_result = "\n".join([str(row) for row in result])
        self.logger.debug(
            f"\nQuery executed successfully. Number of rows returned: {num_rows}"
        )
        self.logger.debug(f"\nQuery Result:\n{formatted_result}")

        # Return an answer to the user
        messages.append(
            {
                "role": RoleTypes.DEVELOPER,
                "content": f"""
                    The user previously asked a question, and a SQL query was executed to retrieve relevant data.
                    The query result is:

                    {formatted_result}

                    Your task is to **write a natural language answer** to the user.
                    Do **NOT** generate another SQL query. Simply provide a clear, well-written summary response.

                    Additionally, if there are multiple data records, display such with a Markdown-formatted table.
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

        return APIResponsePayload(
            data=ChatResponse(
                response=OpenAIMessage(role=RoleTypes.ASSISTANT, content=ai_response)
            ),
            meta=ChatResponseMeta(
                completion_id=completion_id or None,
                executed_query=executed_query or None,
            ),
        )
