from app.logger import get_logger
from app.llm.factory import llm_provider

logger = get_logger(__name__)

class Agent:
    def __init__(self, name: str, instructions: str, tools: list = None):
        self.name = name
        logger.debug(
            "Initialising agent '%s' | tools=%s",
            name,
            [t.__name__ for t in (tools or [])],
        )
        self.chat = llm_provider.create_chat_session(
            system_instruction=instructions,
            tools=tools or []
        )

    def run(self, message: str) -> str:
        logger.debug("Agent '%s' sending message: %s", self.name, message[:120])
        text = self.chat.send_message(message)
        logger.debug("Agent '%s' raw response: %s", self.name, text[:120])
        return text
