import os
from google import genai
from google.genai import types
from app.logger import get_logger

logger = get_logger(__name__)

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_ID=os.getenv("GEMINI_MODEL_ID")

class Agent:
    def __init__(self, name: str, instructions: str, tools: list = None):
        self.name = name
        logger.debug(
            "Initialising agent '%s' | tools=%s",
            name,
            [t.__name__ for t in (tools or [])],
        )
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = GEMINI_MODEL_ID
        self.config = types.GenerateContentConfig(
            system_instruction=instructions,
            tools=tools or [],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=not bool(tools)
            )
        )
        self.chat = self.client.chats.create(
            model=self.model_id,
            config=self.config
        )

    def run(self, message: str) -> str:
        logger.debug("Agent '%s' sending message: %s", self.name, message[:120])
        response = self.chat.send_message(message)
        text = response.text
        logger.debug("Agent '%s' raw response: %s", self.name, text[:120])
        return text
