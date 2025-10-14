import sys
from typing import Any

from loguru import logger as _logger

# Define log format with extensive information and nice formatting
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def configure_logger(level="INFO") -> None:
    """Configure the global Loguru logger.

    Call this once at app startup (e.g., in the FastAPI app factory).
    """
    _logger.remove()
    _logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=level,
        backtrace=False,
        diagnose=False,
    )


def get_logger(**context: Any):
    """Return a context-bound logger for dependency injection.

    Example: `get_logger(service="scraper", request_id=req_id)`
    """
    return _logger.bind(**context)
