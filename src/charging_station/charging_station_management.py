# Dann die Implementation (DDD):
from dataclasses import dataclass 
from datetime import datetime, time 
from enum import Enum 
from typing import List, Optional, field

# Value Objects
@dataclass (frozen=True)
class PostalCode:
    value: str

    def __post_init__(self):
        if not self._is_valid_berlin_postal_code():
            raise InvalidPostalCodeException(
                f"{self. value} ist keine gültige Berliner PLZ"
            )
    
    def _is_valid_berlin_postal_code(self) -> bool:
        return (self.value.startswith(("10", "12", "13"))
            and len(self.value) == 5)

class StationStatus (Enum) :
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"

# Entities
@dataclass
class ChargingStation:
    id: str
    postal_code: PostalCode 
    status: StationStatus
    location: str
    peak_times: List[time] = field(default_factory=list)
    last_status_update: datetime = field(default_factory=datetime.now)

    def update_status(self, new_status: StationStatus) :
        self. status = new_status
        self. last_status_update = datetime. now()

# Domain Events
@dataclass (frozen=True)
class StationsAvailabilityRequested:
    postal_code: PostalCode 
    timestamp: datetime

class InvalidPostalCodeException(Exception):
    pass
