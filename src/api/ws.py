import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.display_state import get_display_state

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/displays/{display_id}")
async def display_state_socket(
    websocket: WebSocket,
    display_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await websocket.accept()

    state = await get_display_state(db, display_id)
    if state is None:
        await websocket.send_json({"type": "error", "detail": "Display not found"})
        await websocket.close(code=1008)
        return

    await websocket.send_json(state)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        return
