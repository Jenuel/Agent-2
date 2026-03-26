from typing import List, Callable, Optional, Any
from google import genai
from google.genai import types

from app.llm.base import BaseLLM, ChatSession
from app.retry import call_with_retry_sync, call_with_retry_async
from app.logger import get_logger

logger = get_logger(__name__)

class GeminiChatSession(ChatSession):
    def __init__(
        self, 
        client: genai.Client, 
        model_id: str, 
        system_instruction: Optional[str] = None, 
        tools: Optional[List[Callable]] = None
    ):
        config_kwargs = {}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if tools:
            config_kwargs["tools"] = tools
            config_kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(disable=False)
            
        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
        self.chat = client.chats.create(model=model_id, config=config)

    def send_message(self, message: str) -> str:
        response = call_with_retry_sync(
            lambda: self.chat.send_message(message),
            label="gemini_chat_session"
        )
        return response.text

class GeminiProvider(BaseLLM):
    def __init__(self, api_key: str, model_id: str):
        if not api_key:
            raise ValueError("API key for Gemini is required.")
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id

    def generate_response_sync(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
        response = call_with_retry_sync(
            lambda: self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config,
            ),
            label="gemini_generate_sync",
        )
        return response.text

    async def generate_response_async(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
        response = await call_with_retry_async(
            lambda: self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config,
            ),
            label="gemini_generate_async",
        )
        return response.text

    def create_chat_session(
        self,
        system_instruction: Optional[str] = None,
        tools: Optional[List[Callable]] = None
    ) -> ChatSession:
        return GeminiChatSession(
            client=self.client,
            model_id=self.model_id,
            system_instruction=system_instruction,
            tools=tools
        )
