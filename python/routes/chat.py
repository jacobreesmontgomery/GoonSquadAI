from fastapi import APIRouter

from models.base import APIResponsePayload, Empty
from models.chat import ChatRequest, ChatResponse
from services.chat import ChatService
from utils.simple_logger import SimpleLogger

chat_service = ChatService()
logger = SimpleLogger(log_level="INFO", class_name=__name__).logger

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
        response_model=APIResponsePayload[ChatResponse, Empty],
    )
    async def process_chat_message(
        request: ChatRequest,
    ) -> APIResponsePayload[ChatResponse, Empty]:
        """
        Retrieves all activities for the authenticated athlete.

        :param request: The request object.

        :return: The chat response.
        """

        logger.info(f"Processing chat message: {request.text}")

        response = chat_service.process(user_question=request.text)

        return APIResponsePayload(data=response, meta=Empty())
