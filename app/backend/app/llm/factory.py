import os
from app.llm.base import BaseLLM
from app.logger import get_logger

logger = get_logger(__name__)

def get_llm_provider() -> BaseLLM:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider == "openai":
        from app.llm.openai_provider import OpenAIProvider
        api_key = os.getenv("OPENAI_API_KEY")
        model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini")
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set.")
        logger.info(f"Initializing OpenAI Provider with model: {model_id}")
        return OpenAIProvider(api_key=api_key, model_id=model_id)
        
    elif provider == "gemini":
        from app.llm.gemini_provider import GeminiProvider
        api_key = os.getenv("GEMINI_API_KEY")
        model_id = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set.")
        logger.info(f"Initializing Gemini Provider with model: {model_id}")
        return GeminiProvider(api_key=api_key, model_id=model_id)
        
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

llm_provider = get_llm_provider()