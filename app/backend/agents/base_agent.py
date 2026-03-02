import os
import google.generativeai as genai
from backend.logger import get_logger

logger = get_logger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class Agent:
    def __init__(self, name: str, instructions: str, tools: list = None):
        self.name = name
        logger.debug(
            "Initialising agent '%s' | tools=%s",
            name,
            [t.__name__ for t in (tools or [])],
        )
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=instructions,
            tools=tools or [],
        )
        self.chat = self.model.start_chat(
            enable_automatic_function_calling=bool(tools)
        )

    def run(self, message: str) -> str:
        logger.debug("Agent '%s' sending message: %s", self.name, message[:120])
        response = self.chat.send_message(message)
        text = response.text
        logger.debug("Agent '%s' raw response: %s", self.name, text[:120])
        return text
