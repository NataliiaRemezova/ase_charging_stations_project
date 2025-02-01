from dataclasses import dataclass 
from datetime import datetime
from backend.src.charging_station_rating.charging_station_rating_service import RatingService, RatingRepository

@dataclass(frozen=True)
class Rating:
    """
    Represents a user rating for a charging station.
    
    Attributes:
        rating_value (int): The rating value between 1 and 5.
        comment (str): The user's comment on the station.
        author_id (str): The ID of the user providing the rating.
        station_id (str): The ID of the charging station being rated.
    
    Raises:
        InvalidRatingException: If the rating is not between 1 and 5.
        InvalidCommentException: If the comment exceeds 500 characters.
    """
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
    """
    Event triggered when a new rating is created.
    
    Attributes:
        station_id (str): The ID of the station being rated.
        user_id (str): The ID of the user providing the rating.
        rating_value (int): The rating value between 1 and 5.
        comment (str): The user's comment.
        timestamp (datetime): The time the rating was created.
    """
    station_id: str 
    user_id: str 
    rating_value: int
    comment: str
    timestamp: datetime

class RatingManagement:
    """
    Handles the creation and management of charging station ratings.
    """
    def __init__(self):
        self.ratingService = RatingService(repository=RatingRepository())

    async def handle_create_rating(self, username, user_id, station_id, rating_value, comment):
        """
        Handle creating a rating, performing validation, and saving it.
        
        Args:
            username (str): The username of the user.
            user_id (str): The ID of the user creating the rating.
            station_id (str): The ID of the station being rated.
            rating_value (int): The rating value between 1 and 5.
            comment (str): The user's comment.
        
        Returns:
            dict: The created rating data.
        
        Raises:
            ValueError: If validation fails.
            Exception: If an error occurs while saving the rating.
        """
        try:
            rating_data = {
                "station_id": station_id,
                "username": username,
                "user_id": user_id,
                "rating_value": rating_value,
                "comment": comment,
            }
            
            result = await self.ratingService.create_rating(rating_data)
            return result
        except ValueError as e:
            print(f"Validation error: {e}")
            raise
        except Exception as e:
            print(f"Error creating rating: {e}")
            raise

class InvalidRatingException(Exception):
    """Exception raised for invalid rating values."""
    pass

class InvalidCommentException(Exception):
    """Exception raised for excessively long comments."""
    pass
