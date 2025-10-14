from fastapi import APIRouter

from .utils import router as utils_router

router = APIRouter()

router.include_router(utils_router)

__all__ = ["router"]
