from dataclasses import dataclass 
from datetime import datetime, time 

class StationSearchService:
    def __init__(self, repository: StationRepository):
        self.repository = repository
        
    def search_by_postal_code(self, code: str) -> SearchResult:
        postal_code = PostalCode(code)
        stations = self.repository.find_by_postal_code(postal_code)
        event = ChargingStationSearched(
            postal_code=postal_code.value, 
            stations_found=len(stations), 
            timestamp=datetime.now()
        )
        return SearchResult(stations=stations, event=event)