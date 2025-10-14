from fastapi import APIRouter

from app.schemas.utils import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(message="OK")
