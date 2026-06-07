import hashlib
import json
import logging
from datetime import date, datetime, timedelta, timezone

from src.ujin_api.news import NewsFetch

logger = logging.getLogger(__name__)


class UjinNewsError(Exception):
    pass


class NewsService:
    def __init__(self, news_fetch: NewsFetch | None = None, ttl_days: int = 7):
        if news_fetch is None:
            news_fetch = NewsFetch()
        self._news_fetch = news_fetch
        self._ttl_days = ttl_days

    async def get_relevant_news_for_building(self, building_id: int) -> list[dict]:
        logger.info("Запрос релевантных новостей: building_id=%s", building_id)
        response = await self._news_fetch.get_news_list(buildings=building_id, type="news")
        if "items" not in response:
            raise UjinNewsError("API новостей Ujin вернул ошибку")

        today = datetime.now(timezone.utc).date()
        min_date = today - timedelta(days=self._ttl_days)
        relevant_items = []

        for item in response["items"]:
            publication_date = self._parse_publication_date(item)
            if publication_date is None:
                continue

            if not self._is_building_relevant(item, building_id):
                logger.debug(
                    "Новость отфильтрована по дому: news_id=%s building_id=%s",
                    item.get("id"),
                    building_id,
                )
                continue

            if min_date <= publication_date <= today:
                relevant_items.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "text": item.get("text"),
                        "date": item.get("date"),
                    }
                )

        relevant_items.sort(key=lambda item: item["date"], reverse=True)
        logger.info(
            "Релевантные новости собраны: building_id=%s count=%s",
            building_id,
            len(relevant_items),
        )
        return relevant_items

    def build_news_signature(self, items: list[dict]) -> str:
        signature_payload = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "text": item.get("text"),
                "date": item.get("date"),
            }
            for item in items
        ]
        serialized_payload = json.dumps(
            signature_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()

    @staticmethod
    def build_news_widget_event(building_id: int, items: list[dict]) -> dict:
        return {
            "type": "widget_updated",
            "widget": "news",
            "building_id": building_id,
            "items": items,
        }

    def _parse_publication_date(self, item: dict) -> date | None:
        raw_date = item.get("date")
        try:
            return date.fromisoformat(raw_date)
        except (TypeError, ValueError):
            logger.warning(
                "Новость пропущена из-за некорректной даты: news_id=%s date=%s",
                item.get("id"),
                raw_date,
            )
            return None

    @staticmethod
    def _is_building_relevant(item: dict, building_id: int) -> bool:
        buildings = item.get("buildings") or []
        if not buildings:
            return True
        return any(building.get("id") == building_id for building in buildings)


news_service = NewsService()
