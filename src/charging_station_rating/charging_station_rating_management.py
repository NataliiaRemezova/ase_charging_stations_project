from dataclasses import dataclass 
from datetime import datetime, time 
from typing import List, Optional, ClassVar
from charging_station_rating.charging_station_rating_service import RatingService

@dataclass(frozen=True)
class Rating:
    rating_value: int
    comment: str
    author_id: str
    station_id: str

    def __post_init__(self) :
        if not 1 <= self.rating_value <= 5:
            raise InvalidRatingException("Rating must be between 1 and 5.")
        if len(self.comment) > 500:
            raise InvalidCommentException("Comment is too long.")

@dataclass(frozen=True)
class RatingCreated:
    station_id: str 
    user_id: str 
    rating_value: int
    comment: str
    timestamp: datetime

class RatingManagement:
    ratingService: ClassVar[RatingService] = RatingService()

    def handle_create_rating(self, userSession, user_id, station_id, rating_value, comment) -> RatingCreated:
        try:
            rating = Rating(rating_value, comment, user_id, station_id)
        except InvalidRatingException as e:
            # Print error message if rating is invalid
            print(str(e))
            return False
        except InvalidCommentException as e:
            # Print error message if comment is invalid
            print(str(e))
            return False
        
        # check if user autheticated via userSession?

        rating_data = {
            "rating_value": rating_value,
            "comment": comment,
            "user_id": user_id,
            "station_id": station_id
        }
        result = self.ratingService.create_rating(rating_data)
        resultEvent = RatingCreated(**result)

        return resultEvent


# Custom exceptions
class InvalidRatingException(Exception):
    pass

class InvalidCommentException(Exception):
    pass

