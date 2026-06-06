from src.core.client_api import ClientAPI


class ParkingFetch:
    def __init__(self, client: ClientAPI | None = None):
        self.base_path = "api/v1/parking"
        if client is None:
            client = ClientAPI()
        self.api = client

    async def get_parkings_list(self, complexes=None, buildings=None):
        endpoint = f"{self.base_path}/list"
        return await self.api.fetch_data(
            endpoint=endpoint,
            **{"complexes[]": complexes, "buildings[]": buildings},
        )
