from charging_station_rating_management import InvalidRatingException, Rating, RatingCreated
from datetime import datetime, time 

class RatingService:
    def __init__(self, repository: RatingRepository):
        self.repository = repository

    def create_rating(self, rating) -> RatingCreated:
        # check is already happening in management
        stars = rating.rating_value
        if stars < 1 or stars > 5:
            raise InvalidRatingException("Rating value must be between 1 and 5.")
        
        self.repository.save_rating(rating.station_id, rating.user_id, stars, rating.comment)
        # Simulate creating a rating
        event = RatingCreated(
            station_id = rating.station_id,
            user_id = rating.user_id,
            rating_value = stars,
            comment = rating.comment,
            timestamp = datetime.now()
        )
        return event