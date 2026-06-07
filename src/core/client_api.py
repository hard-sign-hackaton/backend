import httpx

from src.config import settings


class ClientAPI:
    def __init__(self, timeout: float = 10.0):
        self.url = settings.API_URL.rstrip("/")
        self.api_key = settings.API_KEY
        self.params = {"token": self.api_key}
        self.timeout = timeout
        self.transport = httpx.AsyncHTTPTransport(retries=settings.MAX_RETRIES)

    async def fetch_data(self, endpoint: str, **params):
        request_params = {
            **self.params,
            **{key: value for key, value in params.items() if value is not None},
        }
        endpoint = endpoint.lstrip("/")

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                response = await client.get(f"{self.url}/{endpoint}", params=request_params)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return {"status_code": response.status_code, "data": response.text}
        except httpx.HTTPError as e:
            return {"error": str(e)}
