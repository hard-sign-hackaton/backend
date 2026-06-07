import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Body, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.display_state import display_state_service
from src.services.display_push import display_push_service
from src.services.display_template_service import (
    display_template_service,
    DisplayNotFoundError,
    NoAssignedTemplateError,
)
from src.services.display_service import display_service as display_crud_service, DisplayNotFoundError as DisplayCrudNotFoundError
from src.schemas.display import DisplayCreate, DisplayUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/displays", tags=["displays"])


@router.get("/{display_id}/state")
async def display_state(display_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос состояния дисплея для=%s", display_id)
    state = await display_state_service.get_display_state(db, display_id)
    if state is None:
        logger.warning("Дисплей не найден: %s", display_id)
        raise HTTPException(status_code=404, detail="Дисплей не найден")
    logger.debug("Состояние дисплея найдено для=%s", display_id)
    return state

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_display(
    payload: DisplayCreate, db: AsyncSession = Depends(get_db)
):
    new_display = await display_crud_service.create_display(db, payload)
    return new_display


@router.get("/")
async def list_displays(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    return await display_crud_service.list_displays(db, limit=limit, offset=offset)


@router.get("/{display_id}")
async def get_display_by_id(display_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    d = await display_crud_service.get_display(db, display_id)
    if d is None:
        raise HTTPException(status_code=404, detail="Display not found")
    return d


@router.put("/{display_id}")
async def update_display(
    display_id: uuid.UUID, payload: DisplayUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        updated = await display_crud_service.update_display(db, display_id, payload)
    except DisplayCrudNotFoundError:
        raise HTTPException(status_code=404, detail="Display not found")
    return updated


@router.delete("/{display_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_display(display_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        await display_crud_service.delete_display(db, display_id)
    except DisplayCrudNotFoundError:
        raise HTTPException(status_code=404, detail="Display not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
