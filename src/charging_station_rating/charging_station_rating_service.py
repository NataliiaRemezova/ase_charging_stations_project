from datetime import datetime, time 

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