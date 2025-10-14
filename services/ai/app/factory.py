from fastapi import FastAPI

from app.routes import router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title="Adverse Media Screening AI Service", version="0.1.0")

    app.include_router(router)
    return app
