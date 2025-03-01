from pydantic import BaseModel
from typing import Annotated


class ChatRequest(BaseModel):
    """
    A model representing a chat request.

    :param text: The user question.
    """

    text: Annotated[str, "The user question."]


class ChatRequestMeta(BaseModel):
    """
    A model representing a chat request's metadata.

    :param completion_id: The conversation's completion ID (if an existing chat).
    """

    completion_id: Annotated[int, "The user conversation's completion ID."]


class ChatResponse(BaseModel):
    """
    A model representing a chat response.

    :param response: The AI response to a user question.
    """

    response: Annotated[str, "The AI response to a user question."]


class ChatResponseMeta(BaseModel):
    """
    A model representing the metadata for a chat response.

    :param completion_id: The completion ID.
    """

    completion_id: Annotated[str, "The completion ID of the user-bot exchange."]
