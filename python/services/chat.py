from services.retrievers.tag import TAGRetriever
from models.chat import ChatResponse


class ChatService:
    def __init__(self):
        # Eventually we'll need an intent router to determine which retriever to use
        self.retriever = TAGRetriever()

    def process(self, user_question: str) -> ChatResponse:
        """
        Processes a chat message.

        :param user_question: The user's question.

        :return: The chat response.
        """
        return self.retriever.process(user_question=user_question)
