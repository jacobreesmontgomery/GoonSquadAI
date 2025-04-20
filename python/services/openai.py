from os import getenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

from utils.simple_logger import SimpleLogger


class OpenAIService:
    """
    Handles all OpenAI API requests.
    """

    # Models that support structured outputs with json_schema (as of 4/19/25)
    STRUCTURED_OUTPUT_SUPPORTED_MODELS = [
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini",
        "gpt-4o",
    ]

    def __init__(self, model: str = None):
        """
        Initializes the OpenAI service.

        :param model: The model to use for processing the messages.

        :return: None
        """
        self.client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
        self.model: str = (
            getenv("OPENAI_MODEL", "gpt-4.1-mini") if model is None else model
        )
        self.logger = SimpleLogger(class_name=__name__).logger

    def _supports_structured_output(self, model: str) -> bool:
        """
        Checks if the model supports structured outputs.

        :param model: The model to check.
        :return: True if the model supports structured outputs, False otherwise.
        """
        return any(
            supported in model for supported in self.STRUCTURED_OUTPUT_SUPPORTED_MODELS
        )

    async def process_request(
        self,
        messages: list[dict[str, str]],
        model: str = None,
        use_streaming: bool = False,
        store: bool = True,
        response_schema: dict = None,
    ) -> ChatCompletion:
        """
        Processes a chat request.

        :param messages: The messages to process.
        :param model: The model to use for processing the messages.
        :param use_streaming: Whether to use streaming for processing the messages.
        :param store: Whether to store the messages in the completion.
        :param response_schema: The schema for the response.

        :return: The chat completion response.
        """
        if model is None:
            model = self.model

        # Check if structured output is requested but not supported by the model
        if response_schema and not self._supports_structured_output(model):
            self.logger.warning(
                f"Model {model} does not support structured outputs with json_schema. "
                f"Using standard completion instead."
            )
            response_schema = None

        try:
            response: ChatCompletion = (
                self.client.chat.completions.create(
                    model=model, messages=messages, stream=use_streaming, store=store
                )
                if not response_schema
                else self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=use_streaming,
                    store=store,
                    response_format={
                        "type": "json_schema",
                        "json_schema": response_schema,
                    },
                )
            )
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            raise
        return response
