import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Display, DisplayGroupMember, EmergencyEvent, EmergencyTarget
from src.services.connection_manager import ConnectionManager, connection_manager

logger = logging.getLogger(__name__)


class EmergencyServiceError(Exception):
    pass


class EmergencyService:
    def __init__(self, manager: ConnectionManager):
        self._manager = manager

    async def create_emergency(
        self,
        db: AsyncSession,
        message: str,
        duration_seconds: int,
        display_id: uuid.UUID | None = None,
        display_group_id: uuid.UUID | None = None,
    ) -> tuple[EmergencyEvent, str, list[uuid.UUID]]:
        target_type = self.resolve_target_type(display_id, display_group_id)
        self._validate_create_payload(message, duration_seconds)

        now = datetime.now(timezone.utc)
        emergency = EmergencyEvent(
            message=message,
            starts_at=now,
            ends_at=now + timedelta(seconds=duration_seconds),
        )
        db.add(emergency)
        await db.flush()

        db.add(
            EmergencyTarget(
                emergency_event_id=emergency.id,
                display_id=display_id,
                display_group_id=display_group_id,
                target_type=target_type,
            )
        )
        await db.flush()

        display_ids = await self.get_display_ids_for_target(
            db=db,
            target_type=target_type,
            display_id=display_id,
            display_group_id=display_group_id,
        )
        logger.info(
            "ЧС создана: emergency_id=%s target_type=%s displays_count=%s",
            emergency.id,
            target_type,
            len(display_ids),
        )
        return emergency, target_type, display_ids

    async def get_display_ids_for_target(
        self,
        db: AsyncSession,
        target_type: str,
        display_id: uuid.UUID | None = None,
        display_group_id: uuid.UUID | None = None,
    ) -> list[uuid.UUID]:
        if target_type == "all":
            result = await db.execute(select(Display.id).order_by(Display.id))
            return list(result.scalars().all())

        if target_type == "display":
            if display_id is None:
                raise EmergencyServiceError("Для цели display нужен display_id")
            return [display_id]

        if target_type == "group":
            if display_group_id is None:
                raise EmergencyServiceError("Для цели group нужен display_group_id")
            result = await db.execute(
                select(DisplayGroupMember.display_id)
                .where(DisplayGroupMember.display_group_id == display_group_id)
                .order_by(DisplayGroupMember.display_id)
            )
            return list(result.scalars().all())

        raise EmergencyServiceError(f"Неизвестный target_type: {target_type}")

    async def get_display_ids_for_emergency(
        self,
        db: AsyncSession,
        emergency_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        result = await db.execute(
            select(EmergencyTarget).where(EmergencyTarget.emergency_event_id == emergency_id)
        )
        targets = result.scalars().all()

        display_ids = []
        for target in targets:
            display_ids.extend(
                await self.get_display_ids_for_target(
                    db=db,
                    target_type=target.target_type,
                    display_id=target.display_id,
                    display_group_id=target.display_group_id,
                )
            )

        return list(dict.fromkeys(display_ids))

    async def delete_emergency(
        self,
        db: AsyncSession,
        emergency_id: uuid.UUID,
    ) -> tuple[EmergencyEvent | None, list[uuid.UUID]]:
        emergency = await db.get(EmergencyEvent, emergency_id)
        if emergency is None:
            return None, []

        display_ids = await self.get_display_ids_for_emergency(db, emergency_id)
        await db.execute(
            delete(EmergencyTarget).where(EmergencyTarget.emergency_event_id == emergency_id)
        )
        await db.delete(emergency)
        await db.flush()

        logger.info(
            "ЧС удалена: emergency_id=%s displays_count=%s",
            emergency_id,
            len(display_ids),
        )
        return emergency, display_ids

    def build_emergency_event(
        self,
        display_id: uuid.UUID,
        emergency: EmergencyEvent,
        duration_seconds: int,
    ) -> dict[str, Any]:
        return {
            "type": "emergency_updated",
            "display_id": str(display_id),
            "active": True,
            "emergency": {
                "id": str(emergency.id),
                "message": emergency.message,
                "duration_seconds": duration_seconds,
            },
        }

    @staticmethod
    def build_emergency_reset_event(display_id: uuid.UUID) -> dict[str, Any]:
        return {
            "type": "emergency_updated",
            "display_id": str(display_id),
            "active": False,
            "emergency": None,
        }

    async def send_emergency_to_displays(
        self,
        display_ids: list[uuid.UUID],
        emergency: EmergencyEvent,
        duration_seconds: int,
    ) -> int:
        delivered_count = 0
        for display_id in display_ids:
            message = self.build_emergency_event(display_id, emergency, duration_seconds)
            delivered = await self._manager.send_to_display(display_id, message)
            if delivered:
                delivered_count += 1

        logger.info(
            "ЧС отправлена по WebSocket: emergency_id=%s displays_count=%s delivered_displays=%s",
            emergency.id,
            len(display_ids),
            delivered_count,
        )
        return delivered_count

    async def send_emergency_reset_to_displays(
        self,
        display_ids: list[uuid.UUID],
    ) -> int:
        delivered_count = 0
        for display_id in display_ids:
            message = self.build_emergency_reset_event(display_id)
            delivered = await self._manager.send_to_display(display_id, message)
            if delivered:
                delivered_count += 1

        logger.info(
            "Сброс ЧС отправлен по WebSocket: displays_count=%s delivered_displays=%s",
            len(display_ids),
            delivered_count,
        )
        return delivered_count

    @staticmethod
    def resolve_target_type(
        display_id: uuid.UUID | None,
        display_group_id: uuid.UUID | None,
    ) -> str:
        if display_id is not None and display_group_id is not None:
            raise EmergencyServiceError("Нельзя одновременно передать display_id и display_group_id")
        if display_id is not None:
            return "display"
        if display_group_id is not None:
            return "group"
        return "all"

    @staticmethod
    def _validate_create_payload(message: str, duration_seconds: int) -> None:
        if not message.strip():
            raise EmergencyServiceError("Сообщение ЧС не может быть пустым")
        if duration_seconds <= 0:
            raise EmergencyServiceError("duration_seconds должен быть больше нуля")


emergency_service = EmergencyService(connection_manager)
