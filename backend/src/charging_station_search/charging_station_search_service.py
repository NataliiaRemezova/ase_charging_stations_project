from dataclasses import dataclass 
from datetime import datetime, time 
from bson.objectid import ObjectId
from backend.db.mongo_client import station_collection
from backend.src.charging_station_search.charging_station_search_management import ChargingStation, PostalCode, SearchResult, ChargingStationSearched

class StationRepository:
    async def find_by_postal_code(self, postal_code: PostalCode):
        """
        Query MongoDB for charging stations by postal code.
        """
        try:
            results = await station_collection.find({"postal_code": postal_code.value}).to_list(100)  # Limit results for performance
            return [
                ChargingStation(
                    id=str(station["_id"]),
                    postal_code=PostalCode(station["postal_code"]),
                    availability_status=station["availability_status"],
                    location=f"{station['location']['latitude']}, {station['location']['longitude']}",
                    name=station.get("name", "Unknown Name"),  # Include name field
                )
                for station in results
            ]
        except Exception as e:
            print(f"Error querying stations: {e}")
            return []

class StationSearchService:
    def __init__(self, repository: StationRepository):
        self.repository = repository

    async def search_by_postal_code(self, code: str) -> SearchResult:
        """
        Search for charging stations by postal code.
        """
        postal_code = PostalCode(code)
        # Await the asynchronous repository method
        stations = await self.repository.find_by_postal_code(postal_code)
        event = ChargingStationSearched(
            postal_code=postal_code.value,
            stations_found=len(stations),
            timestamp=datetime.now()
        )
        return SearchResult(stations=stations, event=event)
