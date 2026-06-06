import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.connection_manager import ConnectionManager, connection_manager
from src.services.display_state import DisplayStateService, display_state_service

logger = logging.getLogger(__name__)


class DisplayPushService:
    def __init__(
        self,
        state_service: DisplayStateService,
        manager: ConnectionManager,
    ):
        self._state_service = state_service
        self._manager = manager

    async def push_display_state(self, db: AsyncSession, display_id: uuid.UUID) -> bool:
        logger.info("Пуш состояния дисплея: display_id=%s", display_id)
        state = await self._state_service.get_display_state(db, display_id)
        if state is None:
            logger.warning("Пуш состояния отменен, дисплей не найден: display_id=%s", display_id)
            return False

        delivered = await self._manager.send_to_display(display_id, state)
        if delivered:
            logger.info("Пуш состояния доставлен: display_id=%s", display_id)
        else:
            logger.info("Пуш состояния не доставлен, нет активного подключения: display_id=%s", display_id)
        return delivered


display_push_service = DisplayPushService(display_state_service, connection_manager)
