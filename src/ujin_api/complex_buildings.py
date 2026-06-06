import httpx

from src.core.client_api import ClientAPI


class PropertiesFetch:
    def __init__(self, client: ClientAPI | None = None):
        if client is None:
            client = ClientAPI()
        self.client = client

    async def ComplexList(self):
        try:
            response = await self.client.fetch_data(endpoint="v1/complex/list/")
        except httpx.HTTPError as e:
            return 500, {"error": str(e)}
        if response.get("error") != 0:
            return response
        return {
            "items": [
                self._parse_complex_item(item)
                for item in response.get("data", {}).get("items", [])
            ]
        }

    async def BuildingsGetListCRM(self, per_page=None, page=None, complex_id=None, search=None):
        try:
            response = await self.client.fetch_data(
                endpoint="v1/buildings/get-list-crm/",
                per_page=per_page,
                page=page,
                complex_id=complex_id,
                search=search,
            )
        except httpx.HTTPError as e:
            return 500, {"error": str(e)}
        if response.get("error") != 0:
            return response
        return {
            "items": [
                self._parse_building_item(item)
                for item in response.get("data", {}).get("buildings", [])
            ]
        }

    @staticmethod
    def _parse_complex_item(item: dict) -> dict:
        region = item.get("region") or {}
        return {
            "id": item.get("id"),
            "title": item.get("title"),
            "region_title": region.get("title"),
        }

    @staticmethod
    def _parse_building_item(item: dict) -> dict:
        complex_info = item.get("complex") or {}
        building = item.get("building") or {}
        address = building.get("address") or {}
        return {
            "id": item.get("id") or building.get("id"),
            "title": building.get("title"),
            "complex_id": complex_info.get("id"),
            "complex_title": complex_info.get("title"),
            "timezone": complex_info.get("timezone"),
            "floor": building.get("floor"),
            "apartment_count": building.get("apartmentCount"),
            "entrance_count": building.get("entranceCount"),
            "full_address": address.get("fullAddress"),
            "security_number": building.get("security_number"),
            "paid_tickets_allowed": building.get("paid_tickets_allowed"),
            "entrances": item.get("entrances2") or [],
            "statistics": item.get("statistics") or [],
        }
