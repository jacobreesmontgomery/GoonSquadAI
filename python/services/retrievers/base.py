from abc import ABC, abstractmethod
from models.chat import ChatResponse, ChatResponseMeta
from models.base import APIResponsePayload


class BaseRetriever(ABC):
    """
    Abstract base class that defines the interface for all retrievers.
    """

    @abstractmethod
    async def process(
        self,
        user_question: dict[str, str],
        messages: list[dict[str, str]],
        gpt_model: str = None,
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Process a user question and return a response.

        :param user_question: The user's question.
        :param messages: The conversation history.
        :param gpt_model: Optional model override.
        :return: Response payload with answer and metadata.
        """
        pass
