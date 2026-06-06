import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.display_state import get_display_state

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/displays", tags=["displays"])


@router.get("/{display_id}/state")
async def display_state(display_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос состояния дисплея для=%s", display_id)
    state = await get_display_state(db, display_id)
    if state is None:
        logger.warning("Дисплей не найден: %s", display_id)
        raise HTTPException(status_code=404, detail="Display not found")
    logger.debug("Состояние дисплея найдено для=%s", display_id)
    return state
