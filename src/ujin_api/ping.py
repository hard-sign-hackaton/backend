import httpx

from src.core.client_api import ClientAPI


class PingFetch:
    def __init__(self, client: ClientAPI | None = None):
        self.service = "ping"
        if client is None:
            client = ClientAPI()
        self.client = client

    async def fetch_data(self):
        try:
            return await self.client.fetch_data(self.service)
        except httpx.HTTPError as e:
            return {"error": str(e)}
