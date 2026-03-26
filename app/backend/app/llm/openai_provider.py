import inspect
import json
from typing import List, Callable, Optional, Any, Dict
from openai import OpenAI, AsyncOpenAI

from app.llm.base import BaseLLM, ChatSession
from app.retry import call_with_retry_sync, call_with_retry_async
from app.logger import get_logger

logger = get_logger(__name__)

def _function_to_json_schema(func: Callable) -> Dict[str, Any]:
    sig = inspect.signature(func)
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        param_type = "string"
        if param.annotation == int:
            param_type = "integer"
        elif param.annotation == float:
            param_type = "number"
        elif param.annotation == bool:
            param_type = "boolean"
            
        parameters["properties"][name] = {"type": param_type}
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(name)
            
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or f"Execute {func.__name__}",
            "parameters": parameters,
        }
    }

class OpenAIChatSession(ChatSession):
    def __init__(
        self,
        client: OpenAI,
        model_id: str,
        system_instruction: Optional[str] = None,
        tools: Optional[List[Callable]] = None
    ):
        self.client = client
        self.model_id = model_id
        self.messages = []
        if system_instruction:
            self.messages.append({"role": "system", "content": system_instruction})
            
        self.tools = tools or []
        self.tool_map = {f.__name__: f for f in self.tools}
        self.openai_tools = [_function_to_json_schema(f) for f in self.tools] if self.tools else None
        
    def send_message(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        
        while True:
            kwargs = {
                "model": self.model_id,
                "messages": self.messages,
            }
            if self.openai_tools:
                kwargs["tools"] = self.openai_tools
                kwargs["tool_choice"] = "auto"
                
            response = call_with_retry_sync(
                lambda: self.client.chat.completions.create(**kwargs),
                label="openai_chat_session"
            )
            
            message_obj = response.choices[0].message
            self.messages.append(message_obj.model_dump(exclude_none=True))
            
            if message_obj.tool_calls:
                for tool_call in message_obj.tool_calls:
                    func_name = tool_call.function.name
                    args_str = tool_call.function.arguments
                    logger.info("Executing tool: %s with args: %s", func_name, args_str)
                    
                    try:
                        args = json.loads(args_str)
                        func = self.tool_map.get(func_name)
                        if func:
                            result = func(**args)
                        else:
                            result = f"Error: function {func_name} not found."
                            
                    except Exception as e:
                        logger.error("Error executing tool %s: %s", func_name, e)
                        result = str(e)
                        
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
            else:
                return message_obj.content

class OpenAIProvider(BaseLLM):
    def __init__(self, api_key: str, model_id: str):
        if not api_key:
            raise ValueError("API key for OpenAI is required.")
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model_id = model_id

    def generate_response_sync(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = call_with_retry_sync(
            lambda: self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
            ),
            label="openai_generate_sync"
        )
        return response.choices[0].message.content

    async def generate_response_async(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await call_with_retry_async(
            lambda: self.async_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
            ),
            label="openai_generate_async"
        )
        return response.choices[0].message.content

    def create_chat_session(
        self,
        system_instruction: Optional[str] = None,
        tools: Optional[List[Callable]] = None
    ) -> ChatSession:
        return OpenAIChatSession(
            client=self.client,
            model_id=self.model_id,
            system_instruction=system_instruction,
            tools=tools
        )
