import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from src.models import EmergencyEvent
from src.services.emergency import EmergencyService, emergency_service

logger = logging.getLogger(__name__)


class EmergencyWatcherService:
    def __init__(self, emergency: EmergencyService):
        self._emergency = emergency

    async def reset_expired_emergencies(self, db) -> list[dict]:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(EmergencyEvent)
            .where(
                EmergencyEvent.status == "active",
                EmergencyEvent.ends_at.is_not(None),
                EmergencyEvent.ends_at <= now,
            )
            .order_by(EmergencyEvent.ends_at, EmergencyEvent.created_at)
        )
        emergencies = result.scalars().all()

        results = []
        for emergency in emergencies:
            emergency_id = emergency.id
            deleted_emergency, display_ids = await self._emergency.delete_emergency(db, emergency_id)
            if deleted_emergency is None:
                continue

            await db.commit()
            delivered_count = await self._emergency.send_emergency_reset_to_displays(display_ids)
            results.append(
                {
                    "emergency_id": str(emergency_id),
                    "displays_count": len(display_ids),
                    "delivered_displays": delivered_count,
                }
            )

        if results:
            logger.info("Истекшие ЧС сброшены: emergencies_count=%s", len(results))
        return results

    async def run_polling(
        self,
        session_factory,
        interval_seconds: int,
    ) -> None:
        logger.info("Фоновая проверка ЧС запущена: interval_seconds=%s", interval_seconds)
        try:
            while True:
                try:
                    async with session_factory() as db:
                        await self.reset_expired_emergencies(db)
                except Exception:
                    logger.exception("Ошибка фоновой проверки ЧС")

                await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Фоновая проверка ЧС остановлена")
            raise


emergency_watcher_service = EmergencyWatcherService(emergency_service)
