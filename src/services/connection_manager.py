import logging
import uuid
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)

    @property
    def connected_count(self) -> int:
        return sum(len(connections) for connections in self._connections.values())

    async def connect(self, display_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[display_id].add(websocket)
        logger.info(
            "WebSocket подключен: display_id=%s active_connections=%s",
            display_id,
            self.connected_count,
        )

    def disconnect(self, display_id: uuid.UUID, websocket: WebSocket) -> None:
        connections = self._connections.get(display_id)
        if connections is None:
            logger.debug("WebSocket уже отсутствует в менеджере: display_id=%s", display_id)
            return

        connections.discard(websocket)
        if not connections:
            self._connections.pop(display_id, None)
        logger.info(
            "WebSocket отключен: display_id=%s active_connections=%s",
            display_id,
            self.connected_count,
        )

    async def send_to_display(self, display_id: uuid.UUID, message: dict[str, Any]) -> bool:
        connections = self._connections.get(display_id)
        if not connections:
            logger.info("Нет активных WebSocket-подключений для display_id=%s", display_id)
            return False

        delivered_count = 0
        for websocket in list(connections):
            try:
                await websocket.send_json(message)
                delivered_count += 1
            except Exception:
                logger.exception("Не удалось отправить WebSocket-сообщение: display_id=%s", display_id)
                self.disconnect(display_id, websocket)

        logger.info(
            "WebSocket-сообщение отправлено: display_id=%s delivered_connections=%s",
            display_id,
            delivered_count,
        )
        return delivered_count > 0

    async def broadcast(self, message: dict[str, Any]) -> None:
        logger.info("WebSocket broadcast: displays_count=%s", len(self._connections))
        for display_id in list(self._connections):
            await self.send_to_display(display_id, message)


connection_manager = ConnectionManager()
