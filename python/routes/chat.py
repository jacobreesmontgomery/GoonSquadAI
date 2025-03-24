from fastapi import APIRouter

from models.base import APIRequestPayload, APIResponsePayload, Empty
from models.chat import ChatRequest, ChatRequestMeta, ChatResponse, ChatResponseMeta
from repositories.chat import ChatRepository
from utils.simple_logger import SimpleLogger

chat_repository = ChatRepository()
logger = SimpleLogger(class_name=__name__).logger

chat_router = APIRouter()


class ChatAPI:
    """
    Handles all chat API requests.
    """

    @chat_router.post(
        "/chat",
        summary="Process chat message.",
        description="Process a chat message and return a response.",
        status_code=200,
        response_model=APIResponsePayload[ChatResponse, ChatResponseMeta],
    )
    async def process_chat_message(
        request: APIRequestPayload[ChatRequest, ChatRequestMeta],
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Retrieves all activities for the authenticated athlete.

        :param request: The request object.

        :return The response payload.
        """

        messages: list[dict[str, str]] = request.data.messages_to_dict()
        user_question: dict[str, str] = messages[len(messages) - 1]
        response = await chat_repository.process_chat_message(
            user_question=user_question, messages=messages
        )

        return response
