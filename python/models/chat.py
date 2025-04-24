from pydantic import BaseModel
from typing import Annotated
from enum import Enum


class RoleTypes(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"
    SYSTEM = "system"


# This is based on OpenAI's chat completion 'messages' structure
class OpenAIMessage(BaseModel):
    role: RoleTypes
    content: str

    def to_dict(self):
        """
        Converts the model to a dictionary.
        """
        return {"role": self.role, "content": self.content}


class ChatRequest(BaseModel):
    """
    A model representing a chat request.

    :param messages: A list of messages.
    """

    messages: Annotated[list[OpenAIMessage], "A list of messages."]

    def messages_to_dict(self):
        """
        Returns a list of message dictionaries.
        """
        return [message.to_dict() for message in self.messages]


class ChatRequestMeta(BaseModel):
    """
    A model representing a chat request's metadata.

    :param completion_id: The conversation's completion ID (if an existing chat).
    """

    completion_id: Annotated[int, "The user conversation's completion ID."] = None


class ChatResponse(BaseModel):
    """
    A model representing a chat response.

    :param response: The AI response to a user question.
    """

    response: Annotated[OpenAIMessage, "The AI response to a user question."]


class ChatResponseMeta(BaseModel):
    """
    A model representing the metadata for a chat response.

    :param completion_id: The completion ID.
    """

    completion_id: Annotated[str, "The completion ID of the user-bot exchange."] = None
    executed_query: Annotated[str, "The query that was executed."] = None
    query_results: Annotated[str, "The results of the executed query."] = None
    query_confidence: Annotated[
        str | None,
        "The confidence level of the generated query (LOW, MEDIUM, HIGH).",
    ] = None
    answer_confidence: Annotated[
        str | None,
        "The confidence level of the generated answer (LOW, MEDIUM, HIGH).",
    ] = None


class GeneratedQueryOutput(BaseModel):
    query: Annotated[str, "The generated SQL query."]
    confidence: Annotated[str, "The confidence level of the query (LOW, MEDIUM, HIGH)."]
    follow_ups: Annotated[
        str | None,
        "Follow-up questions to ask the user--in the case of a LOW confidence level--to gain clarity on the request.",
    ] = None
