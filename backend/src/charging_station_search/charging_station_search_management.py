from dataclasses import dataclass 
from datetime import datetime, time 
from typing import List, Optional, ClassVar
from backend.src.charging_station_rating.charging_station_rating_service import RatingService

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


# Exceptions
class InvalidPostalCodeException (Exception):
    """
    Exception raised for invalid postal codes.
    """
    pass