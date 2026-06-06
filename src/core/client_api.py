import httpx
from ..config import settings

class ClientAPI:
    def __init__(self):
        self.url = settings.API_URL
        self.api_key = settings.API_KEY
        self.params = {"token": self.api_key}
                       
                       
    def fetch_data(self, endpoint, **params):
        params = {**self.params, **params}
        try:
            response = httpx.get(f"{self.url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}
    
    