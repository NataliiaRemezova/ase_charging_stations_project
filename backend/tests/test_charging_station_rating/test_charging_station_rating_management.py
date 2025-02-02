"""
test_charging_station_rating_management.py

Description:
    This script contains unit tests for the methods of the charging station rating management in 
    src/charging_station_rating/charging_station_rating_management.py.

Usage:
    It is run with all the other tests in this repo by running 'pytest' in the terminal.

Dependencies:
    pytest, unittest.mock, datetime

Author:
    Nina Immenroth

Date:
    2024-12-26
    updated for async functions 2025-01-30

Version:
    Version 0.2
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from backend.src.charging_station_rating.charging_station_rating_management import (
    RatingManagement,
    InvalidRatingException,
    InvalidCommentException
)
from backend.src.charging_station_rating.charging_station_rating_service import (
    RatingService,
    RatingNotFoundException,
    StationNotFoundException
)

@pytest.fixture
def rating_service_mock():
    """Fixture for a mocked RatingService."""
    service = AsyncMock(spec=RatingService)
    return service

@pytest.mark.asyncio
async def test_handle_create_rating_success(rating_service_mock):
    """TC 1: authenticated user creation of valid rating - success."""
    timestamp = datetime.utcnow().isoformat()

    rating_service_mock.create_rating.return_value = {
        "station_id": "station_123",
        "username": "Hansi",
        "user_id": "user_456",
        "rating_value": 4,
        "comment": "Great station!",
        "timestamp": timestamp
    }

    rating_management = RatingManagement(rating_service_mock)

    result = await rating_management.handle_create_rating(
        username="Hansi",
        user_id="user_456",
        station_id="station_123",
        rating_value=4,
        comment="Great station!"
    )

    assert result["station_id"] == "station_123"
    assert result["user_id"] == "user_456"
    assert result["rating_value"] == 4
    assert result["comment"] == "Great station!"
    assert datetime.fromisoformat(result["timestamp"]).replace(microsecond=0) == datetime.fromisoformat(timestamp).replace(microsecond=0)
    rating_service_mock.create_rating.assert_awaited_once()

@pytest.mark.asyncio
async def test_handle_create_rating_failure_invalid_stars(rating_service_mock):
    """TC 2a: authenticated user creation of rating - failure - wrong amount of stars."""
    rating_management = RatingManagement(rating_service_mock)
    with pytest.raises(InvalidRatingException, match="Rating must be between 1 and 5."):
        await rating_management.handle_create_rating(
            username="Hansi",
            user_id="user_456",
            station_id="station_123",
            rating_value=6,
            comment="Invalid stars"
        )

@pytest.mark.asyncio
async def test_handle_create_rating_failure_invalid_comment(rating_service_mock):
    """TC 2b: authenticated user creation of rating - failure - wrong length of comment."""
    long_comment = "x" * 501  # 501 characters
    rating_management = RatingManagement(rating_service_mock)
    with pytest.raises(InvalidCommentException, match="Comment is too long, can't be longer than 500 characters."):
        await rating_management.handle_create_rating(
            username="Hansi",
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment=long_comment
        )

@pytest.mark.asyncio
async def test_handle_create_rating_general_error(rating_service_mock):
    """TC 3: Test handling general exceptions."""
    rating_service_mock.create_rating.side_effect = Exception("Unexpected error.")

    rating_manager = RatingManagement(rating_service_mock)

    with pytest.raises(Exception, match="Unexpected error."):
        await rating_manager.handle_create_rating(
            username="testuser", 
            user_id="user123", 
            station_id="station123", 
            rating_value=5, 
            comment="Excellent service!"
        )

@pytest.mark.asyncio
async def test_handle_update_rating_success(rating_service_mock):
    """TC 4: authenticated user update of own rating - success."""
    # Stub the update_rating method
    
    timestamp = datetime.utcnow().isoformat()
    rating_service_mock.update_rating.return_value = {
        'rating_value': [4], 
        'comment': ['Updated rating.'],
        'username': 'Hansi', 
        'user_id': 'user_456', 
        'timestamp': timestamp
    }

    rating_management = RatingManagement(rating_service_mock)

    result = await rating_management.handle_update_rating(
        rating_id = "1233",
        rating_value=4,
        comment="Updated rating",
    )

    assert result["username"] == "Hansi"
    assert result["user_id"] == "user_456"
    assert result["rating_value"] == [4]
    assert result["comment"] == ['Updated rating.']
    assert result["timestamp"] == timestamp
    rating_service_mock.update_rating.assert_called_once()

@pytest.mark.asyncio
async def test_handle_update_rating_failure_invalid_stars(rating_service_mock):
    """TC 6a: authenticated user update of own rating - failure - wrong amount of stars."""
    # Test rating value outside valid range
    rating_management = RatingManagement(rating_service_mock)

    with pytest.raises(InvalidRatingException, match="Rating must be between 1 and 5."):
        await rating_management.handle_update_rating(
            rating_id = "1233",
            rating_value= 0,
            comment="Invalid stars",
        )
    with pytest.raises(InvalidRatingException, match="Rating must be between 1 and 5."):
        await rating_management.handle_update_rating(
            rating_id = "1233",
            rating_value= -1,
            comment="Invalid stars",
        )
    with pytest.raises(InvalidRatingException, match="Rating must be between 1 and 5."):
        await rating_management.handle_update_rating(
            rating_id = "1233",
            rating_value= 6,
            comment="Invalid stars",
        )

@pytest.mark.asyncio
async def test_handle_update_rating_failure_invalid_comment(rating_service_mock):
    """TC 6b: authenticated user update of own rating - failure - comment too long."""
    # Test comment length outside valid range
    # the rating
    rating_management = RatingManagement(rating_service_mock)

    long_comment = "x" * 501  # 501 characters

    with pytest.raises(InvalidCommentException, match="Comment is too long, can't be longer than 500 characters."):
        await rating_management.handle_update_rating(
            rating_id = "1233",
            rating_value= 3,
            comment=long_comment,
        )


@pytest.mark.asyncio
async def test_handle_delete_rating_success(rating_service_mock):
    """TC 7: authenticated user deletion of own rating - success."""
    # Stub the delete_rating method
    rating_service_mock.delete_rating.return_value = True

    rating_management = RatingManagement(rating_service_mock)

    result = await rating_management.handle_delete_rating(
        rating_id="123"
    )

    assert result is True
    rating_service_mock.delete_rating.assert_called_once_with(
        "123"
    )

@pytest.mark.asyncio
async def test_handle_view_rating_success(rating_service_mock):
    """TC 9: authenticated user view rating - success."""
    
    # Stub the view_ratings method
    rating_service_mock.get_ratings_by_station.return_value = [
        {
            'id': '679a81eae0f6e750dde52e6d', 
            'rating_value': 3, 
            'comment': 'hmmmm', 
            'username': 'Nataliia', 
            'user_id': '679a7fb4e0f6e750dde52e69', 
            'timestamp': '2025-01-29T19:30:50.953000'
        }, 
        {
            'id': '679e63b44011f938945de1f0', 
            'rating_value': 4, 
            'comment': 'it was better this time', 
            'username': 'Tasneem', 
            'user_id': '679e62c54011f938945de1ef',
            'timestamp': '2025-02-01T18:11:00.906000'
        }
    ]

    rating_management = RatingManagement(rating_service_mock)

    result = await rating_management.handle_get_ratings_by_station(
        station_id="station_bht",
    )

    assert len(result) == 2
    assert result[0]["rating_value"] == 3
    assert result[0]["comment"] == "hmmmm"
    assert result[0]["username"] == "Nataliia"
    assert result[1]["rating_value"] == 4
    assert result[1]["comment"] == "it was better this time"
    assert result[1]["username"] == "Tasneem"
    rating_service_mock.get_ratings_by_station.assert_called_once_with(
        "station_bht",
    )

# not sure if this can happen, but should be checked if the exception is propagated correctly
@pytest.mark.asyncio
async def test_handle_delete_rating_failure_nonexistent_rating(rating_service_mock):
    """TC 10: Update Rating - Rating Does Not Exist in the Database."""
    rating_service_mock.delete_rating.side_effect = RatingNotFoundException("Rating not found.")

    rating_management = RatingManagement(rating_service_mock)

    with pytest.raises(RatingNotFoundException, match="Rating not found."):
        await rating_management.handle_update_rating(
            rating_id = "1233",
            rating_value=3,
            comment="Shit."
        )

@pytest.mark.asyncio
async def test_handle_delete_rating_failure_nonexistent_rating(rating_service_mock):
    """TC 11: Delete Rating - Rating Does Not Exist in the Database."""
    rating_service_mock.delete_rating.side_effect = RatingNotFoundException("Rating not found.")
    rating_management = RatingManagement(rating_service_mock)

    with pytest.raises(RatingNotFoundException, match="Rating not found."):
        await rating_management.handle_delete_rating(
            rating_id = "1233"
        )

@pytest.mark.asyncio
async def test_handle_view_rating_failure_station_not_found(rating_service_mock):
    """TC 12: View Ratings - Station Does Not Exist."""
    rating_service_mock.get_ratings_by_station.side_effect = StationNotFoundException("Station not found.")
    rating_management = RatingManagement(rating_service_mock)

    with pytest.raises(StationNotFoundException, match="Station not found."):
        await rating_management.handle_get_ratings_by_station(
            station_id="nonexistent_station",
        )

@pytest.mark.asyncio
async def test_handle_view_rating_success_empty(rating_service_mock):
    """TC 13: authenticated user view rating - success - no ratings to display."""
    # Stub the view_ratings method to return empty list
    rating_service_mock.get_ratings_by_station.return_value = []
    rating_management = RatingManagement(rating_service_mock)

    result = await rating_management.handle_get_ratings_by_station(
        station_id="station_bht",
    )

    assert len(result) == 0
    rating_service_mock.get_ratings_by_station.assert_called_once_with(
        "station_bht",
    )
