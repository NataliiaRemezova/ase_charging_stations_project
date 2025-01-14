from dataclasses import dataclass 
from datetime import datetime, time 
from typing import List, Optional, ClassVar
from backend.src.charging_station_rating.charging_station_rating_service import RatingService
from backend.src.charging_station.charging_station_management import PostalCode

@dataclass
class ChargingStation:
    """Aggregate Root"""
    id: str
    location: str
    postal_code: PostalCode
    availability_status: bool
    name: Optional[str] = "Unknown Name"
    usage_statistics: float = 0.0

@dataclass(frozen=True)
class ChargingStationSearched:
    """Domain Event"""
    postal_code: str 
    stations_found: int 
    timestamp: datetime

@dataclass 
class SearchResult:
    stations: List[ChargingStation] 
    event: ChargingStationSearched


# Exceptions
class InvalidPostalCodeException (Exception):
    pass