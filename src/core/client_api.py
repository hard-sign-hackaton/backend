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
                response_json = response.json()
                if response_json['error'] != 0: raise Exception(response_json["error"])
                return response_json['data']
            except httpx.HTTPError as e:
                return {"error": str(e)}
    
    