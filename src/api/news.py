import logging

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.news import UjinNewsError, news_service
from src.services.news_watcher import news_watcher_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/relevant")
async def relevant_news(building_id: int = Query(..., gt=0)):
    logger.info("HTTP запрос релевантных новостей: building_id=%s", building_id)
    try:
        items = await news_service.get_relevant_news_for_building(building_id)
    except UjinNewsError:
        logger.exception("Ошибка получения новостей Ujin: building_id=%s", building_id)
        raise HTTPException(status_code=502, detail="Ошибка API новостей Ujin")

    return {"items": items}


@router.post("/dev/push-mock-update")
async def push_mock_news_update(
    building_id: int = Query(121, gt=0),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    items = [
        {
            "id": int(now.timestamp()),
            "title": "Тестовое обновление новостей",
            "text": "<p>Это временное WebSocket-событие для проверки фронта.</p>",
            "date": now.date().isoformat(),
        }
    ]
    message = news_service.build_news_widget_event(building_id, items)
    delivered_count = await news_watcher_service.send_widget_event_to_building(
        db=db,
        building_id=building_id,
        message=message,
    )
    logger.info(
        "Dev-событие новостей отправлено: building_id=%s delivered_displays=%s",
        building_id,
        delivered_count,
    )

    return {
        "sent": delivered_count > 0,
        "delivered_displays": delivered_count,
        "message": message,
    }
