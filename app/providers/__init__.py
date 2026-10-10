from app.config import settings
from app.providers.base import LLMProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
    }

    provider_class = providers.get(settings.llm_provider.lower())

    if provider_class is None:
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    return provider_class()