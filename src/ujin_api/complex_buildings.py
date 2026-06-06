import asyncio

import httpx

from src.core.client_api import ClientAPI


class PropertiesFetch:
    def __init__(self, client: ClientAPI | None = None):
        if client is None:
            client = ClientAPI()
        self.client = client

    async def ComplexList(self):
        try:
            return await self.client.fetch_data(endpoint="v1/complex/list/")
        except httpx.HTTPError as e:
            return 500, {"error": str(e)}

    async def BuildingsGetListCRM(self):
        try:
            return await self.client.fetch_data(endpoint="v1/buildings/get-list-crm/")
        except httpx.HTTPError as e:
            return 500, {"error": str(e)}


