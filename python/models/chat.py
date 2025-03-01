from pydantic import BaseModel
from typing import Annotated


class ChatRequest(BaseModel):
    """
    A model representing a chat request.

    :param text: The user question.
    """

    text: Annotated[str, "The user question."]


class ChatResponse(BaseModel):
    """
    A model representing a chat response.

    :param response: The AI response to a user question.
    """

    response: Annotated[str, "The AI response to a user question."]
