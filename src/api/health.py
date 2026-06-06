import logging

from fastapi import APIRouter
from src.config import settings
from src.schemas.health import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health_check():
    logger.info("Хелсчек вызван")
    return HealthResponse(status="ok", service=settings.APP_NAME)