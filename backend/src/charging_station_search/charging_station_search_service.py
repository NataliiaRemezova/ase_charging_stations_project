from dataclasses import dataclass 
from datetime import datetime, time
from typing import List, Optional 
from bson.objectid import ObjectId
from backend.db.mongo_client import station_collection

@dataclass (frozen=True)
class PostalCode:
    """
    Represents a postal code, ensuring it is a valid Berlin postal code.
    
    Attributes:
        value (str): The postal code string.
    
    Raises:
        InvalidPostalCodeException: If the postal code is not valid for Berlin.
    """
    value: str
    def __post_init__(self):
        if not self._is_valid_berlin_postal_code():
            raise InvalidPostalCodeException(
                f"{self. value} ist keine gültige Berliner PLZ"
            )
    
    def _is_valid_berlin_postal_code(self) -> bool:
        return (self.value.startswith(("10", "12", "13"))
            and len(self.value) == 5)

@dataclass
class ChargingStation:
    """
    Represents a charging station as an aggregate root in the domain model.
    
    Attributes:
        id (str): The unique identifier for the charging station.
        location (str): The physical location of the station.
        postal_code (PostalCode): The postal code where the station is located.
        availability_status (bool): Whether the station is currently available.
        name (Optional[str]): The name of the station (default: "Unknown Name").
        usage_statistics (float): The station's usage statistics (default: 0.0).
    """
    id: str
    location: str
    postal_code: PostalCode
    availability_status: bool
    name: Optional[str] = "Unknown Name"
    usage_statistics: float = 0.0

@dataclass(frozen=True)
class ChargingStationSearched:
    """
    Domain event triggered when a charging station search occurs.
    
    Attributes:
        postal_code (str): The postal code searched for.
        stations_found (int): The number of stations found in the search.
        timestamp (datetime): The timestamp of the search event.
    """
    postal_code: str 
    stations_found: int 
    timestamp: datetime

@dataclass 
class SearchResult:
    """
    Represents the result of a charging station search.
    
    Attributes:
        stations (List[ChargingStation]): A list of charging stations found.
        event (ChargingStationSearched): The event related to the search.
    """
    stations: List[ChargingStation] 
    event: ChargingStationSearched

class StationRepository:
    """
    Repository for accessing charging station data from MongoDB.
    """
    async def find_by_postal_code(self, postal_code: PostalCode):
        """
        Query MongoDB for charging stations by postal code.
        
        Args:
            postal_code (PostalCode): The postal code to search for charging stations.
        
        Returns:
            List[ChargingStation]: A list of matching charging stations.
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
    
    async def find_by_object_id(self, object_id: ObjectId):
        """
        Query MongoDB for charging stations by ObjectId.

        Args:
            object_id (ObjectId): The objectId to search for charging stations.

        Returns:
            ChargingStation or None: The matching charging station, or None if an error occurs.
        """
        try:
            result = await station_collection.find_one({"_id": object_id})
            if result:
                return ChargingStation(
                    id=str(result["_id"]),
                    postal_code=PostalCode(result["postal_code"]),
                    availability_status=result["availability_status"],
                    location=f"{result['location']['latitude']}, {result['location']['longitude']}",
                    name=result.get("name", "Unknown Name"),
                )
            return None
        except Exception as e:
            print(f"Error querying station by ID {object_id}: {e}")
            return None
    
    async def update_availability_status(self, station_id: str):
        """
        Update the availability status of a charging station.
        """
        try:
            station = await self.find_by_object_id(ObjectId(station_id))
            if not station:
                print(f"Station with ID {station_id} not found.")
                return []

            new_status = not station.availability_status
            await station_collection.update_one(
                {"_id": ObjectId(station_id)},
                {"$set": {"availability_status": new_status}}
            )
        except Exception as e:
            print(f"Error updating availability status for {station_id}: {e}")
            return []

class StationSearchService:
    """
    Service for searching charging stations by postal code.
    """
    def __init__(self, repository: StationRepository):
        self.repository = repository
        
    async def find_by_object_id(self, object_id: ObjectId):
        """
        Query MongoDB for charging stations by ObjectId.

        Args:
            object_id (ObjectId): The objectId to search for charging stations.

        Returns:
            ChargingStation or None: The matching charging station, or None if an error occurs.
        """
        return await self.repository.find_by_object_id(object_id)
    
    async def update_availability_status(self, station_id: str):
        """
        Update the availability status of a charging station.
        """
        return await self.repository.update_availability_status(station_id)

    async def search_by_postal_code(self, code: str) -> SearchResult:
        """
        Search for charging stations by postal code.

        Args:
            code (str): The postal code to search for charging stations.

        Returns:
            SearchResult: The search result containing stations and event metadata.
        """
        postal_code = PostalCode(code)

        try:
            stations = await self.repository.find_by_postal_code(postal_code)
            if stations is None:
                stations = []  # Fix: Prevent len(None) error
        except Exception as e:
            print(f"Error searching stations by postal code {code}: {e}")
            stations = []  # Fix: Ensure stations is always a list

        event = ChargingStationSearched(
            postal_code=postal_code.value,
            stations_found=len(stations),  # Now len(stations) won't fail
            timestamp=datetime.now()
        )
        return SearchResult(stations=stations, event=event)


# Exceptions
class InvalidPostalCodeException (Exception):
    """
    Exception raised for invalid postal codes.
    """
    pass

