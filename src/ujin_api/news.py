import logging

from src.core.client_api import ClientAPI

logger = logging.getLogger(__name__)


class NewsFetch:
    def __init__(self, client: ClientAPI | None = None):
        self.base_path = "v1/news"
        if client is None:
            client = ClientAPI()
        self.api = client

    async def get_news_list(self, complexes=None, buildings=None, type: str = "news"):
        endpoint = f"{self.base_path}/list"
        response = await self.api.fetch_data(
            endpoint=endpoint,
            complexes=complexes,
            buildings=buildings,
            type=type,
        )

        if response.get("error") != 0:
            logger.warning("Ujin вернул ошибку при получении списка новостей: %s", response)
            return response

        items = response.get("data", {}).get("items", [])
        return {
            "items": [self._parse_news_item(item) for item in items],
            "meta": response.get("data", {}).get("meta"),
        }

    async def get_news_by_id(self, id: int):
        endpoint = f"{self.base_path}/view"
        return await self.api.fetch_data(
            endpoint=endpoint,
            id=id,
        )

    @staticmethod
    def _parse_news_item(item: dict) -> dict:
        news_type = item.get("type") or {}
        return {
            "id": item.get("id"),
            "title": item.get("title"),
            "text": item.get("text"),
            "date": item.get("date"),
            "type_slug": news_type.get("slug"),
            "buildings": [
                {
                    "id": building.get("id"),
                    "title": building.get("title"),
                }
                for building in item.get("buildings", [])
            ],
        }
