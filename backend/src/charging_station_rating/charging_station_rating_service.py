from datetime import datetime, time 
from backend.db.mongo_client import rating_collection
from bson.objectid import ObjectId


class RatingRepository:
    """
    Repository for handling rating data storage and retrieval in MongoDB.
    """
    async def save_rating(self, station_id: str, username: str, user_id: str, rating_value: int, comment: str):
        """
        Save a rating into MongoDB.
        
        Args:
            station_id (str): The ID of the charging station being rated.
            user_id (str): The ID of the user providing the rating.
            rating_value (int): The rating value between 1 and 5.
            comment (str): The user's comment.
        
        Returns:
            str: The ID of the saved rating.
        """
        rating_data = {
            "station_id": station_id,
            "user_id": user_id,
            "username": username,
            "rating_value": rating_value,
            "comment": comment,
            "timestamp": datetime.utcnow(),
        }
        result = await rating_collection.insert_one(rating_data)
        return str(result.inserted_id)  # Return the ID of the saved rating

    async def get_ratings_by_station(self, station_id: str):
        """
        Retrieve ratings for a specific charging station from MongoDB.
        
        Args:
            station_id (str): The ID of the charging station.
        
        Returns:
            list: A list of rating dictionaries.
        """
        ratings = await rating_collection.find({"station_id": station_id}).to_list(100)
        return [
            {
                "rating_value": rating["rating_value"],
                "comment": rating["comment"],
                "username": rating["username"],
                "user_id": rating["user_id"],
                "timestamp": rating["timestamp"].isoformat(),
            }
            for rating in ratings
        ]


class RatingService:
    """
    Service layer for managing rating-related operations.
    """
    def __init__(self, repository: RatingRepository):
        self.repository = repository

    async def create_rating(self, rating_data: dict) -> dict:
        """
        Create a new rating and save it in the repository.
        
        Args:
            rating_data (dict): The rating details including station ID, user ID, rating value, and comment.
        
        Returns:
            dict: The saved rating data.
        
        Raises:
            ValueError: If rating value is out of range or comment exceeds the character limit.
        """
        # Extract fields from rating_data
        rating_value = rating_data.get("rating_value")
        station_id = rating_data.get("station_id")
        user_id = rating_data.get("user_id")
        username = rating_data.get("username")
        comment = rating_data.get("comment")

        # Validate input (if needed, you can add custom exceptions)
        if not (1 <= rating_value <= 5):
            raise ValueError("Rating value must be between 1 and 5.")
        if len(comment) > 500:
            raise ValueError("Comment must be 500 characters or less.")

        # Save the rating using the repository
        rating_id = await self.repository.save_rating(station_id, username, user_id, rating_value, comment)

        # Return the saved rating data
        return {
            "id": rating_id,
            "station_id": station_id,
            "username": username,
            "user_id": user_id,
            "rating_value": rating_value,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
        }
