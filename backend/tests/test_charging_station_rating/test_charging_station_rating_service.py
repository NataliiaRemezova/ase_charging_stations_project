"""
test_charging_station_rating_service.py

Description:
    This script contains unit tests for the methods of the charging station rating service in 
    src/charging_station_rating/charging_station_rating_service.py.

Usage:
    It is run with all the other tests in this repo by running 'pytest' in the terminal.

Dependencies:
    pytest

Author:
    Nina Immenroth

Date:
    2024-12-25

Version:
    Version 0.1
"""

import pytest
from datetime import datetime
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from charging_station_rating.charging_station_rating_service import RatingService
from charging_station_rating.charging_station_rating_management import InvalidRatingException


class MockRatingRepository:
    """
    Mock implementation of the RatingRepository to simulate database operations.
    """
    def __init__(self):
        self.ratings = []

    async def save_rating(self, station_id: str, user_id: str, rating_value: int, comment: str):
        rating_data = {
            "id": str(len(self.ratings) + 1),
            "station_id": station_id,
            "user_id": user_id,
            "rating_value": rating_value,
            "comment": comment,
            "timestamp": datetime.utcnow(),
        }
        self.ratings.append(rating_data)
        return rating_data["id"]

    async def get_ratings_by_station(self, station_id: str):
        return [rating for rating in self.ratings if rating["station_id"] == station_id]


@pytest.mark.asyncio
async def test_valid_charging_station_rating():
    """
    Test the creation of a valid charging station rating.
    """
    station_id = "123"
    user_id = "456"
    rating_data = {
        "rating_value": 4,
        "station_id": station_id,
        "user_id": user_id,
        "comment": "Sehr gut erreichbar, schnelles Laden",
    }
    repository = MockRatingRepository()
    service = RatingService(repository)

    result = await service.create_rating(rating_data)

    assert result["id"] == "1"  # First rating saved
    assert result["station_id"] == station_id
    assert result["user_id"] == user_id
    assert result["rating_value"] == 4
    assert result["comment"] == "Sehr gut erreichbar, schnelles Laden"


@pytest.mark.asyncio
async def test_invalid_rating_value():
    """
    Test creating a rating with an invalid value (greater than 5).
    """
    station_id = "123"
    user_id = "456"
    rating_data = {
        "rating_value": 6,  # Invalid rating value (>5)
        "station_id": station_id,
        "user_id": user_id,
        "comment": "Invalid rating value test",
    }
    repository = MockRatingRepository()
    service = RatingService(repository)

    with pytest.raises(ValueError, match="Rating value must be between 1 and 5."):
        await service.create_rating(rating_data)


@pytest.mark.asyncio
async def test_get_ratings_by_station():
    """
    Test retrieving ratings for a specific station.
    """
    repository = MockRatingRepository()
    service = RatingService(repository)

    # Add some ratings
    await repository.save_rating("123", "user1", 5, "Great station!")
    await repository.save_rating("123", "user2", 4, "Good experience")
    await repository.save_rating("124", "user3", 3, "Average experience")

    ratings = await repository.get_ratings_by_station("123")

    assert len(ratings) == 2
    assert ratings[0]["rating_value"] == 5
    assert ratings[1]["rating_value"] == 4


# Additional test cases

@pytest.mark.asyncio
async def test_rating_value_lower_than_1():
    """
    Test creating a rating with a value less than 1.
    """
    station_id = "123"
    user_id = "456"
    rating_data = {
        "rating_value": 0,  # Invalid rating value (<1)
        "station_id": station_id,
        "user_id": user_id,
        "comment": "Invalid rating value test",
    }
    repository = MockRatingRepository()
    service = RatingService(repository)

    with pytest.raises(ValueError, match="Rating value must be between 1 and 5."):
        await service.create_rating(rating_data)


@pytest.mark.asyncio
async def test_comment_length_exceeds_limit():
    """
    Test creating a rating with a comment longer than 500 characters.
    """
    station_id = "123"
    user_id = "456"
    long_comment = "A" * 501  # Comment that exceeds the limit
    rating_data = {
        "rating_value": 4,
        "station_id": station_id,
        "user_id": user_id,
        "comment": long_comment,
    }
    repository = MockRatingRepository()
    service = RatingService(repository)

    with pytest.raises(ValueError, match="Comment must be 500 characters or less."):
        await service.create_rating(rating_data)


@pytest.mark.asyncio
async def test_duplicate_rating_by_same_user():
    """
    Test that the system allows multiple ratings by the same user for the same station.
    """
    station_id = "123"
    user_id = "456"
    rating_data_1 = {
        "rating_value": 4,
        "station_id": station_id,
        "user_id": user_id,
        "comment": "Good station",
    }
    rating_data_2 = {
        "rating_value": 5,
        "station_id": station_id,
        "user_id": user_id,
        "comment": "Excellent station",
    }

    repository = MockRatingRepository()
    service = RatingService(repository)

    # First rating
    await service.create_rating(rating_data_1)
    # Second rating (duplicate by same user)
    await service.create_rating(rating_data_2)

    # Retrieve ratings
    ratings = await repository.get_ratings_by_station(station_id)

    assert len(ratings) == 2  # Two ratings from the same user
    assert ratings[0]["comment"] == "Good station"
    assert ratings[1]["comment"] == "Excellent station"


@pytest.mark.asyncio
async def test_get_ratings_for_station_with_no_ratings():
    """
    Test retrieving ratings for a station that has no ratings.
    """
    repository = MockRatingRepository()
    service = RatingService(repository)

    # Try to retrieve ratings for a station with no ratings
    ratings = await repository.get_ratings_by_station("999")

    assert len(ratings) == 0  # No ratings should be returned


@pytest.mark.asyncio
async def test_invalid_station_id():
    """
    Test retrieving ratings for a station with an invalid station ID.
    """
    repository = MockRatingRepository()
    service = RatingService(repository)

    # Try to retrieve ratings with an invalid station ID (non-existent station)
    ratings = await repository.get_ratings_by_station("non_existent_station_id")

    assert len(ratings) == 0  # No ratings should be found
