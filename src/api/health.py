from fastapi import APIRouter
from src.config import settings
from src.schemas.health import HealthResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", service=settings.APP_NAME)