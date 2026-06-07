import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Display, DisplayGroupMember
from src.services.connection_manager import ConnectionManager, connection_manager
from src.services.news import NewsService, news_service

logger = logging.getLogger(__name__)


class NewsWatcherService:
    def __init__(
        self,
        news: NewsService,
        manager: ConnectionManager,
    ):
        self._news = news
        self._manager = manager
        self._last_signatures: dict[int, str] = {}

    async def get_tracked_building_ids(self, db: AsyncSession) -> list[int]:
        result = await db.execute(
            select(Display.ujin_building_id)
            .distinct()
            .order_by(Display.ujin_building_id)
        )
        return list(result.scalars().all())

    async def get_display_ids_for_building(
        self,
        db: AsyncSession,
        building_id: int,
    ) -> list[uuid.UUID]:
        result = await db.execute(
            select(Display.id)
            .where(Display.ujin_building_id == building_id)
            .order_by(Display.id)
        )
        return list(result.scalars().all())

    async def get_display_ids_for_group(
        self,
        db: AsyncSession,
        group_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        result = await db.execute(
            select(DisplayGroupMember.display_id)
            .where(DisplayGroupMember.display_group_id == group_id)
            .order_by(DisplayGroupMember.display_id)
        )
        return list(result.scalars().all())

    async def send_widget_event_to_building(
        self,
        db: AsyncSession,
        building_id: int,
        message: dict[str, Any],
    ) -> int:
        display_ids = await self.get_display_ids_for_building(db, building_id)
        delivered_count = await self._manager.send_to_displays(display_ids, message)
        logger.info(
            "Событие виджета отправлено дисплеям дома: building_id=%s displays_count=%s delivered_displays=%s",
            building_id,
            len(display_ids),
            delivered_count,
        )
        return delivered_count

    async def send_widget_event_to_group(
        self,
        db: AsyncSession,
        group_id: uuid.UUID,
        message: dict[str, Any],
    ) -> int:
        display_ids = await self.get_display_ids_for_group(db, group_id)
        delivered_count = await self._manager.send_to_displays(display_ids, message)
        logger.info(
            "Событие виджета отправлено группе дисплеев: group_id=%s displays_count=%s delivered_displays=%s",
            group_id,
            len(display_ids),
            delivered_count,
        )
        return delivered_count

    async def check_building_news(
        self,
        db: AsyncSession,
        building_id: int,
    ) -> dict[str, Any]:
        items = await self._news.get_relevant_news_for_building(building_id)
        signature = self._news.build_news_signature(items)
        previous_signature = self._last_signatures.get(building_id)
        self._last_signatures[building_id] = signature

        if previous_signature is None:
            logger.info(
                "Сигнатура новостей инициализирована: building_id=%s news_count=%s",
                building_id,
                len(items),
            )
            return {
                "building_id": building_id,
                "changed": False,
                "initialized": True,
                "items_count": len(items),
                "delivered_displays": 0,
            }

        if previous_signature == signature:
            logger.debug("Новости не изменились: building_id=%s", building_id)
            return {
                "building_id": building_id,
                "changed": False,
                "initialized": False,
                "items_count": len(items),
                "delivered_displays": 0,
            }

        message = self._news.build_news_widget_event(building_id, items)
        delivered_count = await self.send_widget_event_to_building(db, building_id, message)
        logger.info(
            "Изменение новостей обработано: building_id=%s news_count=%s delivered_displays=%s",
            building_id,
            len(items),
            delivered_count,
        )
        return {
            "building_id": building_id,
            "changed": True,
            "initialized": False,
            "items_count": len(items),
            "delivered_displays": delivered_count,
        }

    async def check_all_buildings(self, db: AsyncSession) -> list[dict[str, Any]]:
        building_ids = await self.get_tracked_building_ids(db)
        logger.info("Проверка новостей по домам: buildings_count=%s", len(building_ids))

        results = []
        for building_id in building_ids:
            results.append(await self.check_building_news(db, building_id))
        return results


news_watcher_service = NewsWatcherService(news_service, connection_manager)
