import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.display_template_service import (
    display_template_service,
    DisplayNotFoundError,
    NoAssignedTemplateError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.post("/{display_id}/template", status_code=status.HTTP_201_CREATED)
async def accept_template(
    display_id: uuid.UUID,
    layout: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Прием шаблона для дисплея %s", display_id)
    try:
        template = await display_template_service.accept_template(db, display_id, layout)
    except DisplayNotFoundError:
        raise HTTPException(status_code=404, detail="Display not found")

    return {"id": str(template.id), "layout": template.layout}


@router.put("/{display_id}/template")
async def update_template(
    display_id: uuid.UUID,
    layout: dict = Body(..., description="New layout JSON"),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Обновление шаблона для дисплея %s", display_id)
    try:
        template = await display_template_service.update_template(db, display_id, layout)
    except NoAssignedTemplateError:
        raise HTTPException(status_code=404, detail="No template assigned to this display")

    return {"id": str(template.id), "layout": template.layout}


@router.post("/{display_id}/template/send")
async def send_template_to_display(display_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на отправку шаблона дисплею %s", display_id)
    try:
        delivered = await display_template_service.send_template(db, display_id)
    except NoAssignedTemplateError:
        raise HTTPException(status_code=404, detail="No assigned template for this display")
    if not delivered:
        raise HTTPException(status_code=424, detail="Template not delivered — no active connection")
    return {"delivered": True}