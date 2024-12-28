@dataclass 
class ChargingStation:
    """Aggregate Root"""
    id: str
    location: str
    postal_code: PostalCode
    availability_status: bool
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