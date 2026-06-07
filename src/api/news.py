import logging

from fastapi import APIRouter, HTTPException, Query

from src.services.news import UjinNewsError, news_service

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
