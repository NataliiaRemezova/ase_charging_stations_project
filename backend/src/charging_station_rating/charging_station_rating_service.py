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
        return result.inserted_id

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
                "timestamp": rating["timestamp"],
            }
            for rating in ratings
        ]


class RatingService:
    def __init__(self):
        self.repository = RatingRepository()

    def create_rating(self, rating_data: dict) -> dict:
        # check is already happening in management
        #if stars < 1 or stars > 5:
        #    raise InvalidRatingException("Rating value must be between 1 and 5.")

        rating_value = rating_data.get("rating_value")
        station_id = rating_data.get("station_id")
        user_id = rating_data.get("user_id")
        comment = rating_data.get("comment")
        
        self.repository.save_rating(station_id, user_id, rating_value, comment)
        # Simulate creating a rating
        response = rating_data.add({"timestamp": datetime.now()})
        return response
    
class RatingRepository:
    def __init__(self):
        pass