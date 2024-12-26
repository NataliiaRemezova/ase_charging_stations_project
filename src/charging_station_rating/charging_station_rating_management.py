from dataclasses import dataclass 
from datetime import datetime, time 

@dataclass (frozen=True)
class Rating:
    value: int
    comment: str

    def __post_init__(self) :
        if not 1 <= self. value <= 5:
            raise InvalidRatingException("Rating muss zwischen 1 und 5 sein.")
        if len(self. comment) > 500:
            raise InvalidRatingException("Kommentar zu lang")

@dataclass (frozen=True)
class RatingCreated:
    station_id: str 
    user_id: str 
    rating_value: int
    comment: str
    timestamp: datetime

#class RatingService:
#    def __init__(self, repository: RatingRepository):