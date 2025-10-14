from fastapi import FastAPI

from app.routes import router
from app.utils.logger import configure_logger


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    configure_logger()
    app = FastAPI(title="Adverse Media Screening AI Service", version="0.1.0")

    app.include_router(router)
    return app
