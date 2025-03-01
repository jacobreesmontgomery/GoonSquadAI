from fastapi import APIRouter, Request

from utils.simple_logger import SimpleLogger

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
        status_code={
            200: "Successfully processed the chat message.",
            400: "Invalid request data.",
            401: "Unauthorized request.",
            403: "Forbidden request.",
            404: "Resource not found.",
            500: "Internal server error.",
        },
    )
    async def process_chat_message(self, request: Request):
        """
        Retrieves all activities for the authenticated athlete.
        """
        # TODO: Implement this method
        logger.info("Processing chat message")
        pass
