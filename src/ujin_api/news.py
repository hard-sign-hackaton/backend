from src.core.client_api import ClientAPI


class NewsFetch:
    def __init__(self, client: ClientAPI | None = None):
        self.base_path = "v1/news"
        if client is None:
            client = ClientAPI()
        self.api = client

    async def get_news_list(self):
        endpoint = f"{self.base_path}/list"
        return await self.api.fetch_data(
            endpoint=endpoint,
        )
        
    async def get_news_by_id(self, id: int):
        endpoint = f"{self.base_path}/view"
        return await self.api.fetch_data(
            endpoint=endpoint,
            **{"id" : id},
        )
