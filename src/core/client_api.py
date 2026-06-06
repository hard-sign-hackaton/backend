import httpx
from ..config import settings
from fastapi import HTTPException

class ClientAPI:
    def __init__(self):
        self.url = settings.API_URL
        self.api_key = settings.API_KEY
        self.params = {"token": self.api_key}
                       
                       
    async def fetch_data(self, endpoint, **params):
        params = {**self.params, **params}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.url}/{endpoint.lstrip('/')}", params=params)
                response.raise_for_status()
                if response['error'] == "1": raise HTTPException(404)
                return response.json()
            except httpx.HTTPError as e:
                return {"error": str(e)}
    
    