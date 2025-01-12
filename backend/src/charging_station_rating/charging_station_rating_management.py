from dataclasses import dataclass 
from datetime import datetime, time 
from typing import List, Optional, ClassVar
from backend.src.charging_station_rating.charging_station_rating_service import RatingService, RatingRepository

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
    def __init__(self):
        self.ratingService = RatingService(repository=RatingRepository())

    async def handle_create_rating(self, userSession, user_id, station_id, rating_value, comment):
        """
        Handle creating a rating, performing validation, and saving.
        """
        try:
            rating_data = {
                "station_id": station_id,
                "user_id": user_id,
                "rating_value": rating_value,
                "comment": comment,
            }
            # Use the service to create the rating
            result = await self.ratingService.create_rating(rating_data)
            return result
        except ValueError as e:
            print(f"Validation error: {e}")
            raise
        except Exception as e:
            print(f"Error creating rating: {e}")
            raise

# Custom exceptions
class InvalidRatingException(Exception):
    pass

class InvalidCommentException(Exception):
    pass
