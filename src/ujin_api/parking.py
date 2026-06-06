from ..core.client_api import ClientAPI

class ParkingFetch:
    def __init__(self):
        self.base_path = 'api/v1/parking'
        self.api = ClientAPI()

    async def get_parkings_list(self, complexes=None, buildings=None):
        endpoint = f"{self.base_path}/list"
        return await self.api.fetch_data(endpoint=endpoint, complexes=complexes, buildings=buildings)
    
    