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
            raise InvalidCommentException("Comment is too long, can't be longer than 500 characters.")

@dataclass(frozen=True)
class RatingCreated:
    station_id: str 
    user_id: str 
    rating_value: int
    comment: str
    timestamp: datetime

class RatingManagement:
    ratingService: ClassVar[RatingService] = RatingService()

    def handle_create_rating(self, userSession:dict, user_id: str, station_id:str , rating_value:int, comment:str) -> RatingCreated:
        # get user_id from the userSession? 
        # check if user autheticated via userSession?
        try:
            rating = Rating(rating_value, comment, user_id, station_id)
        except InvalidRatingException as e:
            # Print error message if rating is invalid or should the error be raised?
            print(str(e))
            return False
        except InvalidCommentException as e:
            # Print error message if comment is invalid
            print(str(e))
            return False

        rating_data = {
            "rating_value": rating_value,
            "comment": comment,
            "user_id": user_id,
            "station_id": station_id
        }
        result = self.ratingService.create_rating(rating_data, userSession)
        resultEvent = RatingCreated(**result)

        return resultEvent
    
    def handle_update_rating(self, userSession:dict, rating:Rating, rating_value:int, comment:str) -> RatingUpdated:
        pass

    def handle_view_ratings(self, userSession:dict, station_id:str) -> List[Rating]:
        pass

    def handle_delete_rating(self, userSession:dict, rating:Rating) -> bool:
        return True


# Custom exceptions
class InvalidRatingException(Exception):
    pass

class InvalidCommentException(Exception):
    pass

