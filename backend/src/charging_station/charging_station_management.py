from dataclasses import dataclass 
from datetime import datetime, time 
from enum import Enum 
from typing import List, Optional 
from dataclasses import field

# Value Objects
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

class StationStatus (Enum):
    """
    Enum representing the possible statuses of a charging station.
    """
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"

# Entities
@dataclass
class ChargingStation:
    """
    Represents a charging station entity.
    
    Attributes:
        id (str): The unique identifier for the charging station.
        postal_code (PostalCode): The postal code where the station is located.
        status (StationStatus): The current status of the station.
        location (str): A description of the station's location.
        peak_times (List[time]): List of peak usage times.
        last_status_update (datetime): Timestamp of the last status update.
    """
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
    """
    Event triggered when charging station availability is requested.
    
    Attributes:
        postal_code (PostalCode): The postal code for the request.
        timestamp (datetime): The time of the request.
    """
    postal_code: PostalCode 
    timestamp: datetime

class InvalidPostalCodeException(Exception):
    """
    Exception raised for invalid Berlin postal codes.
    """
    pass