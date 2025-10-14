from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    # Root directory of the AI service (defaults to "/app" in container)
    project_root: Path = Path(__file__).resolve().parents[1]

    # Processing
    output_dir: Path = Path("downloads")
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
