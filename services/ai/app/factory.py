from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.utils.logger import configure_logger


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    configure_logger()
    app = FastAPI(title="Adverse Media Screening AI Service", version="0.1.0")

    # Add CORS middleware to allow browser requests from localhost
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://localhost:\d+",  # Allow any localhost port
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app
