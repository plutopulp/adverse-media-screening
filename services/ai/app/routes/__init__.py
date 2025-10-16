from fastapi import APIRouter

from .screening import router as screening_router
from .test import router as test_router
from .utils import router as utils_router

router = APIRouter()

router.include_router(screening_router)
router.include_router(test_router)
router.include_router(utils_router)

__all__ = ["router"]
