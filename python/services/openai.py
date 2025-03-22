from os import getenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, stop_after_attempt, wait_random_exponential

from utils.simple_logger import SimpleLogger


class OpenAIService:
    """
    Handles all OpenAI API requests.
    """

    def __init__(self, model: str = None):
        """
        Initializes the OpenAI service.

        :param model: The model to use for processing the messages.

        :return: None
        """
        self.client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
        self.model: str = (
            getenv("OPENAI_MODEL", "gpt-4o-mini") if model is None else model
        )
        self.logger = SimpleLogger(log_level="INFO", class_name=__name__).logger

    def process_request(
        self,
        messages: list[dict[str, str]],
        model: str = None,
        use_streaming: bool = False,
        store: bool = True,
    ) -> ChatCompletion:
        """
        Processes a chat request.

        :param messages: The messages to process.
        :param model: The model to use for processing the messages.
        :param use_streaming: Whether to use streaming for processing the messages.
        :param store: Whether to store the messages in the completion.

        :return: The chat completion response.
        """
        if model is None:
            model = self.model
        response: ChatCompletion = self.client.chat.completions.create(
            model=model, messages=messages, stream=use_streaming, store=store
        )
        return response
