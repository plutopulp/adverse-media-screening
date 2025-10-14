"""
LLM factory for creating language model instances.

"""

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import LLMProviderType, LLMConfig, Settings

LLM_MAPPINGS: dict[LLMProviderType, BaseChatModel] = {
    LLMProviderType.OPENAI: ChatOpenAI,
    LLMProviderType.ANTHROPIC: ChatAnthropic,
}


def create_llm(
    provider: LLMProviderType,
    model: str,
    api_key: str,
    temperature: float = 0.0,
) -> BaseChatModel:
    """
    Factory for creating LLM instances. All configs pre-loaded from settings.


    """
    return LLM_MAPPINGS[provider](model=model, temperature=temperature, api_key=api_key)


def select_llm_config(settings: Settings) -> tuple[LLMProviderType, LLMConfig]:
    cfg_map: dict[LLMProviderType, LLMConfig] = {
        LLMProviderType.OPENAI: settings.openai,
        LLMProviderType.ANTHROPIC: settings.anthropic,
    }
    provider = settings.default_llm_provider
    return provider, cfg_map[provider]
