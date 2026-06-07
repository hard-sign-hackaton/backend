import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.emergency import CreateEmergencyRequest
from src.services.emergency import EmergencyServiceError, emergency_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/emergency", tags=["emergency"])


@router.post("")
async def create_emergency(
    payload: CreateEmergencyRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        emergency, target_type, display_ids = await emergency_service.create_emergency(
            db=db,
            message=payload.message,
            duration_seconds=payload.duration_seconds,
            display_id=payload.display_id,
            display_group_id=payload.display_group_id,
        )
        await db.commit()
    except EmergencyServiceError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    delivered_count = await emergency_service.send_emergency_to_displays(
        display_ids=display_ids,
        emergency=emergency,
        duration_seconds=payload.duration_seconds,
    )
    logger.info(
        "HTTP ЧС создана: emergency_id=%s target_type=%s delivered_displays=%s",
        emergency.id,
        target_type,
        delivered_count,
    )

    return {
        "id": str(emergency.id),
        "message": emergency.message,
        "duration_seconds": payload.duration_seconds,
        "target_type": target_type,
        "display_id": str(payload.display_id) if payload.display_id else None,
        "display_group_id": str(payload.display_group_id) if payload.display_group_id else None,
        "delivered_displays": delivered_count,
    }


@router.delete("/{emergency_id}")
async def delete_emergency(
    emergency_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    emergency, display_ids = await emergency_service.delete_emergency(db, emergency_id)
    if emergency is None:
        raise HTTPException(status_code=404, detail="ЧС не найдена")

    await db.commit()
    delivered_count = await emergency_service.send_emergency_reset_to_displays(display_ids)
    logger.info(
        "HTTP ЧС удалена: emergency_id=%s delivered_displays=%s",
        emergency_id,
        delivered_count,
    )

    return {
        "id": str(emergency_id),
        "deleted": True,
        "delivered_displays": delivered_count,
    }
