from pydantic import BaseModel


class LLMMetadata(BaseModel):
    """Base metadata for all LLM-based stages."""

    # Timing
    processed_at: str  # ISO timestamp
    processing_time_seconds: float | None = None

    # LLM configuration
    llm_provider: str | None = None  # "openai" / "anthropic"
    llm_model: str | None = None  # "gpt-4o" / "claude-4-5-sonnet"

    # Versioning
    analyser_version: str | None = None  # e.g. "0.4.2"
    prompt_version: str | None = None
