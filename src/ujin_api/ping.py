import httpx
from ..core.client_api import ClientAPI


class PingFetch():
    def __init__(self):
        self.service = "ping"
    
    async def fetch_data(self):
        async with httpx.AsyncClient() as client:
            try:
                url = f"{ClientAPI().url}/{self.service}"
                response = await client.get(url, params=ClientAPI().params)
                response.raise_for_status()
                print(response.status_code)
            except httpx.HTTPError as e:
                print("Ping failed:", str(e))
                