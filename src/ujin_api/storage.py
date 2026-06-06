from src.core.client_api import ClientAPI


class StorageFetch:
    def __init__(self, client: ClientAPI | None = None):
        self.base_path = "api/v1/storage"
        if client is None:
            client = ClientAPI()
        self.api = client

    async def get_storage_list(self, complexes=None, buildings=None):
        endpoint = f"{self.base_path}/list"
        return await self.api.fetch_data(
            endpoint=endpoint,
            **{"complexes[]": complexes, "buildings[]": buildings},
        )
        
    async def get_storage(self, type:str,  complexes=None, buildings=None):
        endpoint = f"{self.base_path}/{type}"
        return await self.api.fetch_data(
            endpoint=endpoint,
            **{"complexes[]": complexes, "buildings[]": buildings},
        )
    
    async def get_number_of_type(self, type: str, complexes=None, buildings=None):
        result = await self.get_storage(type, complexes=complexes, buildings=buildings)
        items = result['data'].get('items', [])
        
        complex_list = None
        if complexes is not None:
            complex_list = [complexes] if not isinstance(complexes, list) else complexes
        
        building_list = None
        if buildings is not None:
            building_list = [buildings] if not isinstance(buildings, list) else buildings
        
        count = 0
        for complex_item in items:
            if complex_list is not None and complex_item.get('complex_id') not in complex_list:
                continue
            
            for building in complex_item.get('buildings', []):
                if building_list is not None and building.get('building_id') not in building_list:
                    continue
                
                for storage in building.get('storages', []):
                    if storage.get('assignment_type') == type:
                        count += 1
        return count