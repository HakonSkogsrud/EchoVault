from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from config import ModelConfig


@lru_cache(maxsize=1)
def get_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=ModelConfig.model,
        temperature=ModelConfig.temperature,
        thinking_level=ModelConfig.thinking_level,
    )
