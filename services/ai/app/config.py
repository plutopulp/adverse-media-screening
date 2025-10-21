"""
Configuration management using Pydantic Settings.

This module handles all application settings including LLM provider configurations,
processing parameters, etc..
"""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

# Application version - increment when ScreeningResult schema changes
APP_VERSION = "1.0.0"


class LLMProviderType(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    model: str
    api_key: str
    temperature: float = 0.0


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables use double underscore for nested configs:
    - OPENAI__MODEL=gpt-4o
    - OPENAI__API_KEY=sk-...
    - ANTHROPIC__MODEL=claude-3-5-sonnet-20241022
    - ANTHROPIC__API_KEY=sk-ant-...
    """

    environment: str = "development"
    # Root directory of the AI service (defaults to "/app" in container)
    project_root: Path = Path(__file__).resolve().parents[1]

    # Pre-configure both providers (load API keys at startup)
    openai: LLMConfig = LLMConfig(model="gpt-4o", api_key="", temperature=0.0)
    anthropic: LLMConfig = LLMConfig(
        model="claude-3-5-sonnet-20241022", api_key="", temperature=0.0
    )

    # Default provider to use
    default_llm_provider: LLMProviderType = LLMProviderType.OPENAI

    # Processing
    log_level: str = "INFO"

    model_config = {
        "env_file": [".env.defaults", ".env.secrets"],
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",  # Enable nested env var parsing
        "extra": "ignore",  # Ignore extra fields in env files
    }
