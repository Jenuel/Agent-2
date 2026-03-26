from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Dict, Any

class ChatSession(ABC):
    @abstractmethod
    def send_message(self, message: str) -> str:
        """Send a message and get the response, maintaining chat history."""
        pass

class BaseLLM(ABC):
    @abstractmethod
    def generate_response_sync(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate a single response synchronously."""
        pass

    @abstractmethod
    async def generate_response_async(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate a single response asynchronously."""
        pass
        
    @abstractmethod
    def create_chat_session(
        self,
        system_instruction: Optional[str] = None,
        tools: Optional[List[Callable]] = None
    ) -> ChatSession:
        """Create a stateful chat session."""
        pass
