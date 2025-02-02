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
        timestamp (datetime): The time the rating was created or updated.
    
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
            raise InvalidCommentException("Comment is too long, can't be longer than 500 characters.")

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
    def __init__(self, ratingService: RatingService):
        self.ratingService = ratingService

    async def handle_get_ratings_by_station(self, station_id: str) -> list:
        """
        Retrieve ratings for a specific charging station from the StationService.
        
        Args:
            station_id (str): The ID of the charging station.
        
        Returns:
            list: A list of rating dictionaries.
        """
        try:
            ratings = await self.ratingService.get_ratings_by_station(station_id)
        except Exception as e:
            print(f"Error getting ratings: {e}")
            raise
        return ratings
    
    async def handle_get_rating_by_id(self, rating_id: str):
        """
        Retrieve a specific rating by its ID from MongoDB.
        
        Args:
            rating_id (str): The ID of the rating to retrieve.
        
        Returns:
            dict: The rating data, or None if not found.
        """
        rating = await self.ratingService.get_rating_by_id(rating_id)
        return rating

    async def handle_create_rating(self, username, user_id, station_id, rating_value, comment) -> RatingCreated:
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
            #create a Rating for the value checks
            rating = Rating(rating_value, comment, user_id, station_id)
            rating_data = {
                "station_id": station_id,
                "username": username,
                "user_id": user_id,
                "rating_value": rating_value,
                "comment": comment,
            }
            
            result = await self.ratingService.create_rating(rating_data)
            return result
        except InvalidRatingException as e:
            raise
        except InvalidCommentException as e:
            raise
        except Exception as e:
            print(f"Error creating rating: {e}")
            raise

    async def handle_update_rating(self, rating_id: str, comment: str = None, rating_value: int = None) -> dict:
        """
        Update an existing rating.
        
        Args:
            rating_id (str): The ID of the rating to update.
            rating_value (int, optional): The new rating value.
            comment (str, optional): The new comment.
        
        Returns:
            dict: The updated rating data.
        
        Raises:
            ValueError: If rating value is out of range or comment exceeds the character limit.
        """
        # Validate input for update, get value from tuple
        if isinstance(rating_value, tuple):
            check_value = rating_value[0]
        else: check_value = rating_value
        if not (1 <= check_value <= 5):
            raise InvalidRatingException("Rating must be between 1 and 5.")
        if len(comment) > 500:
            raise InvalidCommentException("Comment is too long, can't be longer than 500 characters.")

        # Perform the update in the service
        try:
            updated_rating = await self.ratingService.update_rating(rating_id, rating_value, comment)
        except ValueError as e:
            raise
        return updated_rating

    async def handle_delete_rating(self, rating_id: str) -> bool:
            """
            Delete an existing rating.
            
            Args:
                rating_id (str): The ID of the rating to delete.
            
            Returns:
                bool: True if the deletion was successful, False otherwise.
            """
            return await self.ratingService.delete_rating(rating_id)

# Custom exceptions
class InvalidRatingException(Exception):
    """Exception raised for invalid rating values."""
    pass

class InvalidCommentException(Exception):
    """Exception raised for too long comments."""
    pass
