import uuid
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)

    @property
    def connected_count(self) -> int:
        return sum(len(connections) for connections in self._connections.values())

    async def connect(self, display_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[display_id].add(websocket)

    def disconnect(self, display_id: uuid.UUID, websocket: WebSocket) -> None:
        connections = self._connections.get(display_id)
        if connections is None:
            return

        connections.discard(websocket)
        if not connections:
            self._connections.pop(display_id, None)

    async def send_to_display(self, display_id: uuid.UUID, message: dict[str, Any]) -> bool:
        connections = self._connections.get(display_id)
        if not connections:
            return False

        for websocket in list(connections):
            await websocket.send_json(message)
        return True

    async def broadcast(self, message: dict[str, Any]) -> None:
        for display_id in list(self._connections):
            await self.send_to_display(display_id, message)
