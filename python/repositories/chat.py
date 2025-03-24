from services.chat import ChatService


class ChatRepository:

    def __init__(self):
        self.chat_service = ChatService()

    async def process_chat_message(
        self, user_question: dict[str, str], messages: list[dict[str, str]]
    ):
        """
        Process a chat message and return a response.

        :param user_question: The user's question.
        :param messages: The messages.

        :return The response payload.
        """

        response = await self.chat_service.process(
            user_question=user_question, messages=messages
        )

        return response
