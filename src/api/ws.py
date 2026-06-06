import logging
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.connection_manager import connection_manager
from src.services.display_state import display_state_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/displays/{display_id}")
async def display_state_socket(
    websocket: WebSocket,
    display_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    logger.info("WebSocket подключение запрошено: display_id=%s", display_id)
    await connection_manager.connect(display_id, websocket)

    state = await display_state_service.get_display_state(db, display_id)
    if state is None:
        logger.warning("WebSocket закрыт, дисплей не найден: display_id=%s", display_id)
        await websocket.send_json({"type": "error", "detail": "Display not found"})
        connection_manager.disconnect(display_id, websocket)
        await websocket.close(code=1008)
        return

    await websocket.send_json(state)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket клиент отключился: display_id=%s", display_id)
        connection_manager.disconnect(display_id, websocket)
        return
