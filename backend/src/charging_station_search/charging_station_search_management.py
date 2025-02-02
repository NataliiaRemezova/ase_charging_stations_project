from bson import ObjectId
from backend.src.charging_station_search.charging_station_search_service import SearchResult, StationRepository, StationSearchService

class StationSearchManagement:
    """
    Handles the creation and management of charging station ratings.
    """
    def __init__(self):
        self.stationService = StationSearchService(repository=StationRepository())
    
    async def search_by_postal_code(self, code: str) -> SearchResult:
        """
        Search for charging stations by postal code.

        Args:
            code (str): The postal code to search for charging stations.

        Returns:
            SearchResult: The search result containing stations and event metadata.
        """
        return await self.stationService.search_by_postal_code(code)
    
    async def find_by_object_id(self, object_id: ObjectId):
        """
        Query MongoDB for charging stations by ObjectId.

        Args:
            object_id (ObjectId): The objectId to search for charging stations.

        Returns:
            ChargingStation or None: The matching charging station, or None if an error occurs.
        """
        return await self.stationService.find_by_object_id(object_id)

    async def update_availability_status(self, station_id: str):
        """
        Update the availability status of a charging station.

        Args:
            station_id (str): The unique identifier of the charging station.
        """
        return await self.stationService.update_availability_status(station_id)
    
    