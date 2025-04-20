from sqlalchemy import text, Sequence, Row, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from json import loads
import logging
from openai.types.chat import ChatCompletion

from prompts.tag import (
    tag_prompt,
    tag_prompt_concise,
    tag_response_schema,
)
from models.athlete import Activity, Athlete
from models.chat import (
    ChatResponse,
    ChatResponseMeta,
    OpenAIMessage,
    RoleTypes,
    GeneratedQueryOutput,
)
from models.base import APIResponsePayload
from models.exceptions import (
    QueryExecutionException,
    QueryGenerationException,
)
from services.database import DatabaseService
from services.openai import OpenAIService
from utils.simple_logger import SimpleLogger
from services.retrievers.base import BaseRetriever


class TAGRetriever(BaseRetriever):
    """
    Handles the TAG (Text-to-SQL-to-Answer Generation) mechanism to retrieve athlete's training data.
    Uses a prompt with built-in reasoning capabilities to handle both simple and complex questions.
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
        self.schema_description: str = self._establish_schema_description()
        self.db_service: DatabaseService = db_service
        self.openai_service: OpenAIService = openai_client
        self.error_msg: str = ""
        self.logger = SimpleLogger(class_name=__name__).logger

    def _establish_schema_description(self) -> str:
        """
        Establishes the schema description for the TAG prompt.

        :return: The schema description.
        """
        activity_desc = Activity().convert_to_schema_description()
        athlete_desc = Athlete().convert_to_schema_description()
        schema_desc = f"{activity_desc}\n{athlete_desc}"
        return schema_desc

    def _clean_query(self, query: str) -> str:
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
        before_sleep=before_sleep_log(
            SimpleLogger(class_name=__name__).logger, logging.INFO
        ),
    )
    async def execute_query(
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
        :param gpt_model: The GPT model to use for generating the query.

        :return: The query results, the number of results, the completion ID, and the query to execute,
                    OR follow-up questions to ask the user.
        """

        if not schema_desc:
            schema_desc = self.schema_description

        # Generate a query based on the user's question
        if self.error_msg:
            messages.append({"role": RoleTypes.DEVELOPER, "content": self.error_msg})

        # Consideration: Use full prompt for the start of the conversation, and the concise equivalent for the rest.
        prompt_content = tag_prompt.format(
            schema_description=schema_desc,
            conversation=messages,
            user_question=user_question,
        )

        messages.append(
            {
                "role": RoleTypes.DEVELOPER,
                "content": prompt_content,
            }
        )

        self.logger.debug(f"Messages being fed in to the LLM:\n{messages}")
        query_result: ChatCompletion = await self.openai_service.process_request(
            messages=messages,
            model=gpt_model if gpt_model else self.openai_service.model,
            response_schema=tag_response_schema,
        )
        completion_id = query_result.id
        self.logger.debug(f"Chat completed: {completion_id}")

        try:
            response_content = query_result.choices[0].message.content
            response_content = response_content.replace("```", "").replace("json", "")
            # Parse the JSON-formatted string into a Python dict
            json_result_data = loads(response_content)
            json_result = GeneratedQueryOutput.parse_obj(json_result_data)

            follow_ups = json_result.follow_ups if json_result.follow_ups else None
            confidence = json_result.confidence
            if confidence == "LOW":
                if not follow_ups:
                    follow_ups = "Could you please elaborate on your question?"
                self.error_msg = f"Confidence level is {confidence}. Follow-up questions: {follow_ups}."
                self.logger.error(self.error_msg)
                return follow_ups
            query_to_execute = self._clean_query(json_result.query)
        except Exception as e:
            self.error_msg = f"An error occurred during query generation: {query_result.choices[0].message.content}: {e}\nPlease try again.\n"
            self.logger.error(self.error_msg)
            raise QueryGenerationException(
                message=self.error_msg
            )  # Hit the retry mechanism

        # Execute the query using async session
        async with self.db_service.get_async_session() as session:
            try:
                self.logger.debug(
                    f"\nExecuting this generated query: {query_to_execute}"
                )
                query_result = await session.execute(text(query_to_execute))
                result = query_result.fetchall()
            except Exception as e:
                self.error_msg = f"An error occurred while executing query [{query_to_execute}]: {e}\nPlease generate a query to resolve this issue.\n"
                self.logger.error(self.error_msg)
                raise QueryExecutionException(
                    message=self.error_msg
                )  # Hit the retry mechanism

        return result, len(result), completion_id, query_to_execute

    async def generate_natural_language_response(
        self,
        messages: list[dict[str, str]],
        result: tuple[Sequence[Row[Any]], int, int, str],
        gpt_model: str = None,
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Generates a natural language response based on query results.

        :param messages: The conversation messages.
        :param result: The query result tuple containing data, row count, completion ID, and executed query.
        :param gpt_model: Optional model to use.

        :return: The API response payload.
        """
        # Unpack the tuple result
        data, num_rows, completion_id, executed_query = result

        # Display the results
        formatted_result = "\n".join([str(row) for row in data])
        self.logger.debug(
            f"\nQuery executed successfully. Number of rows returned: {num_rows}"
        )
        self.logger.debug(f"\nQuery Result:\n{formatted_result}")

        # Return an answer to the user
        response_prompt = f"""
            The user previously asked a question, and a SQL query was executed to retrieve relevant data.
            The query result is:

            {formatted_result}

            Your task is to **write a natural language answer** to the user.
            Do **NOT** generate another SQL query. Simply provide a clear, well-written summary response.

            When presenting data, convert technical values to human-friendly formats:
            - Convert pace in seconds per mile to MM:SS per mile format (e.g., 495 seconds → 8:15 min/mile)
            - Format large values with appropriate commas and units (e.g., 26400 feet → 5.0 miles)
            - Round decimal values to 2 places unless precision is critical
            - Use clear labels for all metrics (e.g., "Average Pace" instead of "avg_pace_s_per_mi")

            Additionally, if there are multiple data records, display such with a Markdown-formatted table.
        """

        messages.append({"role": RoleTypes.DEVELOPER, "content": response_prompt})

        response: ChatCompletion = await self.openai_service.process_request(
            messages=messages,
            model=gpt_model if gpt_model else self.openai_service.model,
        )
        ai_response = response.choices[0].message.content
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

    async def process(
        self,
        user_question: dict[str, str],
        messages: list[dict[str, str]],
        gpt_model: str = None,
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Processes both simple and complex TAG queries using the built-in reasoning capabilities
        of the TAG prompt, which already includes a 3-step ANALYZE, PLAN, and GENERATE approach.

        :param user_question: The user's most recent question.
        :param messages: The list of messages.
        :param gpt_model: The GPT model to use for generating the query (e.g., "gpt-4o-mini").

        :return The response payload.
        """
        try:
            result = await self.execute_query(
                user_question=user_question, messages=messages, gpt_model=gpt_model
            )
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return APIResponsePayload(
                data=ChatResponse(
                    response=OpenAIMessage(
                        role=RoleTypes.ASSISTANT,
                        content="An error occurred during processing. Please try again.",
                    )
                ),
                meta=ChatResponseMeta(
                    completion_id=None,
                    executed_query=None,
                ),
            )

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

        # Generate natural language response from the query results
        return await self.generate_natural_language_response(
            messages=messages,
            result=result,
            gpt_model=gpt_model,
        )
