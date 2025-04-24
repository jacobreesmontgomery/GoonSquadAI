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
    nl_response_schema,
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
    ) -> tuple[Sequence[Row[Any]], int, int, str, str] | str:
        """
        Executes the generated SQL query and returns the results.

        :param user_question: The user's question.
        :param messages: The list of messages.
        :param schema_desc: The schema description for the database.
        :param gpt_model: The GPT model to use for generating the query.

        :return: The query results, the number of results, the completion ID, the query to execute, and the confidence level,
                    OR follow-up questions to ask the user.
        """

        self.logger.debug(
            f"\n\n================In execute_query with user question: {user_question}"
        )

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
            query_confidence = json_result.confidence
            if query_confidence == "LOW":
                if not follow_ups:
                    follow_ups = "Could you please elaborate on your question?"
                self.error_msg = f"Confidence level is {query_confidence}. Follow-up questions: {follow_ups}."
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
        query_execution_exception = None
        result = None
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
                # Store the exception to be raised outside the context manager
                query_execution_exception = QueryExecutionException(
                    message=self.error_msg
                )
        # Re-raise the exception outside the context manager so it can be caught by the retry decorator
        if query_execution_exception:
            self.logger.error(
                f"Raising query execution exception: {query_execution_exception}"
            )
            raise query_execution_exception

        return result, len(result), completion_id, query_to_execute, query_confidence

    async def generate_natural_language_response(
        self,
        messages: list[dict[str, str]],
        result: tuple[Sequence[Row[Any]], int, int, str, str],
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
        data, num_rows, completion_id, executed_query, query_confidence = result

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

            Your task is to **write a natural language answer** to the user and provide a confidence rating for your answer.
            Do **NOT** generate another SQL query. Simply provide a clear, well-written summary response.

            When presenting data, convert technical values to human-friendly formats:
            - Running metrics:
              - avg_pace_sec_per_mi OR avg_pace_s_per_mile: Convert seconds to MM:SS per mile format (e.g., 571 → 9:31 min/mile)
              - avg_speed_ft_s or max_speed_ft_s: Convert feet per second to minutes per mile pace (e.g., 12 ft/s → 7:20 min/mile)
              - moving_time_s or total_moving_time_s: Convert seconds to HH:MM:SS format (e.g., 3600 seconds → 1:00:00)
              - distance_mi or total_distance_mi: Format with 2 decimal places for shorter runs, 1 decimal for longer runs (e.g., 3.25 miles, 26.2 miles)
              - total_elev_gain_ft or elevation_gain or total_elevation_gain_ft: Show both feet and meters (e.g., 500 ft / 152m)
            
            - Other metrics:
              - hr_avg or avg_heart_rate: Present as "Average heart rate: X bpm"
              - spm_avg: Present as "Average cadence: X steps/minute" 
              - For rating scales (rating, sleep_rating, perceived_exertion): Add context (e.g., "Sleep rating: 8/10")
              - For suffer_score: Indicate this is Strava's relative effort metric
              - Round all decimal values to 2 places unless precision is critical

            - Use meaningful labels (e.g., "Average Pace" instead of avg_pace_s_per_mi or avg_pace_sec_per_mi)
            - For runs with wkt_type: Identify the run type (0 = default run, 1 = race, 2 = long run, 3 = workout)
            - When displaying dates (full_datetime), use a friendly format like "Tuesday, January 15, 2023"
            - If athlete name is present, always display that instead of athlete ID.
            
            For monthly summary data (e.g., monthly running statistics):
            - If the data includes "month" or timestamp fields with month information:
              - Display month names fully (e.g., "January" not "Jan" or "01")
              - Convert run_count or total_runs or number of runs to simple integer format
              - Moving time should be in HH:MM:SS format
              - Total distance should be in miles with appropriate precision
              - Average pace should ALWAYS be in MM:SS per mile format, not seconds or any other unit
              - Elevation should always include both feet and meters

            For data that contains avg_pace_sec_per_mi or similar pace fields:
            1. Convert from seconds to MM:SS format (e.g., 571 seconds → 9:31 min/mile)
            2. NEVER present pace as decimal minutes or raw seconds
            3. Example calculation: 
               - 571 seconds = 9 minutes and 31 seconds = 9:31 min/mile
               - 495 seconds = 8 minutes and 15 seconds = 8:15 min/mile

            If there are multiple data records, organize them in a Markdown-formatted table with appropriate column headers and units already converted to human-readable formats.
            
            For example, a monthly running progress table should have headers like:
            | Month | Number of Runs | Total Distance (miles) | Moving Time | Average Pace (min/mile) | Elevation Gain (ft/m) |
            
            DO NOT display raw seconds for pace or raw seconds for moving time in your response. Always convert these values to human-readable formats before presenting them.
            
            IMPORTANT: Your response must be in JSON format with two keys:
            1. "answer": Your natural language response with all the data properly formatted
            2. "confidence": Your confidence level in the answer as one of: "LOW", "MEDIUM", "HIGH"
            
            Use "LOW" if the data is sparse, unclear, or may not fully answer the question.
            Use "MEDIUM" if the data seems relevant but may be incomplete or require assumptions.
            Use "HIGH" if the data directly and completely answers the user's question.
        """

        messages.append({"role": RoleTypes.DEVELOPER, "content": response_prompt})

        response: ChatCompletion = await self.openai_service.process_request(
            messages=messages,
            model=gpt_model if gpt_model else self.openai_service.model,
            response_schema=nl_response_schema,
        )

        response_content = response.choices[0].message.content
        try:
            parsed_response = loads(response_content)
            ai_response: str = parsed_response["answer"]
            response_confidence: str = parsed_response["confidence"]
        except Exception as e:
            self.logger.error(f"Error parsing structured response: {e}")
            ai_response = response_content
            response_confidence = "MEDIUM"

        self.logger.debug(f"\n{ai_response}")
        self.logger.debug(f"Response confidence: {response_confidence}")

        return APIResponsePayload(
            data=ChatResponse(
                response=OpenAIMessage(role=RoleTypes.ASSISTANT, content=ai_response)
            ),
            meta=ChatResponseMeta(
                completion_id=completion_id or None,
                executed_query=executed_query or None,
                query_results=formatted_result or None,
                query_confidence=query_confidence or None,
                answer_confidence=response_confidence or None,
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
                    confidence="LOW",
                ),
            )

        # Generate natural language response from the query results
        return await self.generate_natural_language_response(
            messages=messages,
            result=result,
            gpt_model=gpt_model,
        )
