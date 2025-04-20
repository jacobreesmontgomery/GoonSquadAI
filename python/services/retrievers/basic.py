from services.retrievers.base import BaseRetriever
from services.openai import OpenAIService
from models.chat import ChatResponse, ChatResponseMeta, OpenAIMessage, RoleTypes
from models.base import APIResponsePayload
from utils.simple_logger import SimpleLogger


class BasicRetriever(BaseRetriever):
    """
    A simple retriever for handling general, non-training related questions.
    This retriever doesn't use any specialized data retrieval - it just forwards
    the user query directly to the LLM.
    """

    def __init__(self, openai_client: OpenAIService = None):
        """
        Initialize the basic retriever.

        :param openai_client: Optional OpenAI service client
        """
        self.openai_service = openai_client or OpenAIService()
        self.logger = SimpleLogger(class_name=__name__).logger

    async def process(
        self,
        user_question: dict[str, str],
        messages: list[dict[str, str]],
        gpt_model: str = None,
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Process a general, non-training related question.

        :param user_question: The user's question
        :param messages: The conversation history
        :param gpt_model: Optional model override
        :return: Response payload with answer
        """
        try:
            # Pass the conversation directly to the OpenAI service
            response = await self.openai_service.process_request(
                messages=messages,
                model=gpt_model if gpt_model else self.openai_service.model,
            )

            ai_response = response.choices[0].message.content
            completion_id = response.id

            self.logger.debug(f"Basic retriever processed question: {user_question}")

            return APIResponsePayload(
                data=ChatResponse(
                    response=OpenAIMessage(
                        role=RoleTypes.ASSISTANT, content=ai_response
                    )
                ),
                meta=ChatResponseMeta(
                    completion_id=completion_id,
                    executed_query=None,  # No SQL query for basic retriever
                ),
            )

        except Exception as e:
            self.logger.error(f"Error in basic retriever: {e}")
            return APIResponsePayload(
                data=ChatResponse(
                    response=OpenAIMessage(
                        role=RoleTypes.ASSISTANT,
                        content="I'm sorry, I encountered an error processing your question. Could you please try again?",
                    )
                ),
                meta=ChatResponseMeta(
                    completion_id=None,
                    executed_query=None,
                ),
            )
