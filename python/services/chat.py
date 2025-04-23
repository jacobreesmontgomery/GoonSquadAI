from json import loads
from json.decoder import JSONDecodeError
from openai.types.chat import ChatCompletion

from services.retrievers.tag import TAGRetriever
from services.retrievers.basic import BasicRetriever
from models.chat import ChatResponse, ChatResponseMeta
from models.base import APIResponsePayload
from models.athlete import Activity
from .openai import OpenAIService


class ChatService:
    def __init__(self):
        """Initialize the chat service with appropriate retrievers"""
        self.tag_retriever = TAGRetriever()
        self.basic_retriever = BasicRetriever()
        self.openai_service = OpenAIService()

    async def process(
        self,
        user_question: dict[str, str],
        messages: list[dict[str, str]],
        model: str = None,
    ) -> APIResponsePayload[ChatResponse, ChatResponseMeta]:
        """
        Processes a chat message by routing to the appropriate retriever.

        :param user_question: The user's question.
        :param messages: The conversation messages.
        :param model: Optional model to use for response generation.

        :return The response payload.
        """

        # Determine if this is a training data related question
        if await self._is_training_data_query(
            question=user_question.get("content"), messages=messages
        ):
            return await self.tag_retriever.process(
                user_question=user_question, messages=messages, gpt_model=model
            )
        else:
            # For non-training data questions, use the basic retriever
            return await self.basic_retriever.process(
                user_question=user_question, messages=messages, gpt_model=model
            )

    async def _is_training_data_query(
        self, question: str, messages: list[dict[str, str]]
    ) -> bool:
        """
        Determines if a question is likely about training data and should be handled by TAG.
        Uses GPT-4o-mini to analyze both the question and conversation history.

        :param question: The user's question
        :param messages: The conversation history
        :return: Boolean indicating if this is a training data question
        """
        try:
            system_prompt = """
            **INSTRUCTIONS**:
            - You are a classifier that determines if a question is about running, workouts, 
            training data, or similar athletic activities. Respond with a JSON object containing 'is_training_related' 
            and 'confidence' values, where 'is_training_related' is true if the question is related to running or training data,
            and 'confidence' is a string indicating the confidence level (low, medium, high) of the classification.

            **DATABASE SCHEMA**:
            {database_activities_schema}

            **CLASSIFICATION GUIDELINES**:
            - Training-related topics include: running, workouts, distance, pace, 
              miles, jogging, fitness activities, heart rate, Strava data, races, cardio, steps, elevation,
              athletic performance metrics, run rating, power, sleep, perceived exertion, etc.
              
            - Questions about training progress, athletic history, workout comparisons,
              activity summaries, or performance analysis should return true.
              
            - Questions about general topics unrelated to athletic activities (weather, news, 
              etc.) should return false.
            
            - ANY question about sleep quality, power metrics, personal bests, perceived exertion, elevation gain, 
              or any athletic metric is ALWAYS training-related.
              
            - If a person's name is mentioned with any athletic metric, it is ALWAYS training-related.
            
            - References to any database columns (listed above) such as moving_time_s, distance_mi, avg_speed_ft_s, 
              hr_avg, perceived_exertion, sleep_rating, avg_power, etc., indicate a training-related query.
            
            **EXAMPLES**:
            | Question | Classification |
            | --- | --- |
            | "How many miles did I run last week?" | {{"is_training_related": true, "confidence": "high"}} |
            | "How has my running improved over the last month?" | {{"is_training_related": true, "confidence": "high"}} |
            | "How was my last week of training?" | {{"is_training_related": true, "confidence": "high"}} |
            | "Show me my fastest runs of 2024" | {{"is_training_related": true, "confidence": "high"}} |
            | "How has Jacob's running power improved over the last month?" | {{"is_training_related": true, "confidence": "high"}} |
            | "How was Jacob's sleep in 2023?" | {{"is_training_related": true, "confidence": "high"}} |
            | "What's my average power on hills?" | {{"is_training_related": true, "confidence": "high"}} |
            | "Did I sleep well before my last race?" | {{"is_training_related": true, "confidence": "high"}} |
            | "What's the weather like today?" | {{"is_training_related": false, "confidence": "high"}} |
            | "Can you help me with my homework?" | {{"is_training_related": false, "confidence": "high"}} |
            | "How do I improve my training?" | {{"is_training_related": true, "confidence": "high"}} |
            """.format(
                database_activities_schema=Activity().convert_to_schema_description()
            )

            # Include recent conversation history (last 3 messages) if available
            conversation_context = ""
            if messages and len(messages) > 0:
                recent_messages = messages[-min(3, len(messages)) :]
                conversation_context = "Recent conversation:\n" + "\n".join(
                    [
                        f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                        for msg in recent_messages
                    ]
                )

            current_question = f"Current question: {question}"
            user_prompt = f"{conversation_context}\n\n{current_question}\n\nIs this question related to running?"
            response: ChatCompletion = await self.openai_service.process_request(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model="gpt-4o-mini",
                store=False,
                response_schema={
                    "name": "classification_result",
                    "description": "Indicates if the question is related to running/training data.",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "is_training_related": {
                                "type": "boolean",
                                "description": "True if the question is related to running/training data.",
                            },
                            "confidence": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Confidence level of the classification.",
                            },
                        },
                        "required": ["is_training_related", "confidence"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            )

            # Parse the response
            content = response.choices[0].message.content
            try:
                result: dict = loads(content)
                # Consider medium or high confidence training-related questions as training-related
                return result.get("is_training_related", False) and result.get(
                    "confidence", "low"
                ) in ["medium", "high"]
            except JSONDecodeError:
                # If not valid JSON, check for "true" or "yes" in the response
                return "true" in content.lower() or "yes" in content.lower()

        except Exception as e:
            print(f"Error in training query classification: {str(e)}")
            # Fall back to keyword matching if API call fails
            training_keywords = [
                "run",
                "running",
                "workout",
                "distance",
                "pace",
                "mile",
                "miles",
                "training",
                "exercise",
                "jog",
                "jogging",
                "fitness",
                "activity",
                "activities",
                "time",
                "duration",
                "speed",
                "heart rate",
                "HR",
                "strava",
                "race",
                "races",
                "ran",
                "cardio",
                "track",
                "trail",
                "power",
                "sleep",
                "perceived exertion",
                "exertion",
                "effort",
                "suffer score",
                "score",
                "elevation",
                "gain",
                "performance",
                "steps",
                "avg_power",
                "sleep_rating",
                "kudos",
                "achievement",
                "calories",
            ]

            # Check if question contains keywords related to training data
            for keyword in training_keywords:
                if keyword.lower() in question.lower():
                    return True

            return False
