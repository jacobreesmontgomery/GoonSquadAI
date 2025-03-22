from fastapi import APIRouter

from models.base import APIRequestPayload, APIResponsePayload, Empty
from models.chat import ChatRequest, ChatRequestMeta, ChatResponse, ChatResponseMeta
from services.chat import ChatService
from utils.simple_logger import SimpleLogger

chat_service = ChatService()
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

        logger.info(
            f"Processing the most recent message from these messages: {request.data.messages}"
        )
        messages: list[dict[str, str]] = request.data.messages_to_dict()
        user_question: dict[str, str] = messages[len(messages) - 1]
        response_payload = chat_service.process(
            user_question=user_question, messages=messages
        )
        logger.info(f"Chat message processed.")

        return response_payload
