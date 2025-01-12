from datetime import datetime, time 
from backend.db.mongo_client import rating_collection
from bson.objectid import ObjectId


class RatingRepository:
    async def save_rating(self, station_id: str, user_id: str, rating_value: int, comment: str):
        """
        Save a rating into MongoDB.
        """
        rating_data = {
            "station_id": station_id,
            "user_id": user_id,
            "rating_value": rating_value,
            "comment": comment,
            "timestamp": datetime.utcnow(),
        }
        result = await rating_collection.insert_one(rating_data)
        return str(result.inserted_id)  # Return the ID of the saved rating

    async def get_ratings_by_station(self, station_id: str):
        """
        Retrieve ratings for a specific charging station from MongoDB.
        """
        ratings = await rating_collection.find({"station_id": station_id}).to_list(100)
        return [
            {
                "rating_value": rating["rating_value"],
                "comment": rating["comment"],
                "user_id": rating["user_id"],
                "timestamp": rating["timestamp"].isoformat(),
            }
            for rating in ratings
        ]


class RatingService:
    def __init__(self, repository: RatingRepository):
        self.repository = repository

    async def create_rating(self, rating_data: dict) -> dict:
        """
        Create a new rating and save it in the repository.
        """
        # Extract fields from rating_data
        rating_value = rating_data.get("rating_value")
        station_id = rating_data.get("station_id")
        user_id = rating_data.get("user_id")
        comment = rating_data.get("comment")

        # Validate input (if needed, you can add custom exceptions)
        if not (1 <= rating_value <= 5):
            raise ValueError("Rating value must be between 1 and 5.")
        if len(comment) > 500:
            raise ValueError("Comment must be 500 characters or less.")

        # Save the rating using the repository
        rating_id = await self.repository.save_rating(station_id, user_id, rating_value, comment)

        # Return the saved rating data
        return {
            "id": rating_id,
            "station_id": station_id,
            "user_id": user_id,
            "rating_value": rating_value,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
        }
