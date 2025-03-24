from services.retrievers.tag import TAGRetriever
from models.chat import ChatResponse, ChatResponseMeta, OpenAIMessage
from models.base import APIResponsePayload


class ChatService:
    def __init__(self):
        # Eventually we'll need an intent router to determine which retriever to use
        self.retriever = TAGRetriever()

    async def process(
        self, user_question: dict[str, str], messages: list[dict[str, str]]
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Processes a chat message.

        :param user_question: The user's question.
        :param messages: The conversation messages.

        :return The response payload.
        """

        return await self.retriever.process(
            user_question=user_question, messages=messages
        )
