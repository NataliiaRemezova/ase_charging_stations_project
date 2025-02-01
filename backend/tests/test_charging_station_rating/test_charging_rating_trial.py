import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from charging_station_rating.charging_station_rating_management import (
    Rating,
    RatingManagement,
    RatingCreated,
    InvalidRatingException,
    InvalidCommentException
)
from charging_station_rating.charging_station_rating_service import (
    RatingService,
    RatingNotFoundException,
    StationNotFoundException,
    DoubleRatingException
)

@pytest.fixture
def rating_service_mock():
    """Fixture for a mocked RatingService."""
    service = AsyncMock(spec=RatingService)
    return service

@pytest.mark.asyncio
async def test_handle_create_rating_success(rating_service_mock):
    """Test successful rating creation."""
    rating_service_mock.create_rating.return_value = {
        "station_id": "station123",
        "username": "testuser",
        "user_id": "user123",
        "rating_value": 4,
        "comment": "Great service!"
    }

    rating_manager = RatingManagement(rating_service_mock)
    
    result = await rating_manager.handle_create_rating(
        username="testuser", 
        user_id="user123", 
        station_id="station123", 
        rating_value=4, 
        comment="Great service!"
    )

    assert result["rating_value"] == 4
    assert result["comment"] == "Great service!"
    rating_service_mock.create_rating.assert_called_once()

@pytest.mark.asyncio
async def test_handle_create_rating_invalid_rating_exception(rating_service_mock):
    """Test handling InvalidRatingException."""
    rating_service_mock.create_rating.side_effect = InvalidRatingException("Invalid rating value.")

    rating_manager = RatingManagement(rating_service_mock)

    with pytest.raises(InvalidRatingException):
        await rating_manager.handle_create_rating(
            username="testuser", 
            user_id="user123", 
            station_id="station123", 
            rating_value=10,  # Invalid rating value
            comment="Great service!"
        )

@pytest.mark.asyncio
async def test_handle_create_rating_invalid_comment_exception(rating_service_mock):
    """Test handling InvalidCommentException."""
    rating_service_mock.create_rating.side_effect = InvalidCommentException("Invalid comment.")

    rating_manager = RatingManagement(rating_service_mock)

    with pytest.raises(InvalidCommentException):
        await rating_manager.handle_create_rating(
            username="testuser", 
            user_id="user123", 
            station_id="station123", 
            rating_value=5, 
            comment=""
        )

@pytest.mark.asyncio
async def test_handle_create_rating_general_error(rating_service_mock):
    """Test handling general exceptions."""
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

def test_handle_update_rating_success(rating_management, rating_service_mock):
    """TC 4: authenticated user update of own rating - success."""
    # Stub the update_rating method
    
    timestamp = datetime.now()
    rating_service_mock.update_rating.return_value = {
        "rating_value": 4,
        "comment": "Updated rating.",
        "user_id": "user_456",
        "station_id": "station_bht",
        "timestamp": timestamp
    }

    rating_management = RatingManagement(rating_service_mock)

    # the rating before
    rating = Rating(rating_value=5, 
                    comment="The old rating!", 
                    user_id="user_456", 
                    station_id="station_bht")

    result = rating_management.handle_update_rating(
        username="Hansi",
        rating=rating,
        rating_value=5,
        comment="Updated rating",
    )

    assert result.station_id == "station_bht"
    assert result.user_id == "user_456"
    assert result.rating_value == 4
    assert result.comment == "Updated rating."
    assert result.timestamp == timestamp
    rating_service_mock.update_rating.assert_called_once()

def test_handle_update_rating_failure_other_users_rating(rating_management):
    """TC 5: authenticated user update of other users rating - failure."""
    # Simulate a permission error, but we are not doing it because the error needs to be raised by the management class.
    # mock_rating_service.update_rating.side_effect = PermissionError("Cannot update another user's rating.")

    # the rating
    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="other_user", 
                    station_id="station_bht")
    
    with pytest.raises(PermissionError, match="Cannot update another user's rating."):
        rating_management.handle_update_rating(
            rating=rating,  # Belongs to another user
            rating_value=3,
            comment="Trying to update another user's rating",
        )

def test_handle_update_rating_failure_invalid_stars(rating_management):
    """TC 6a: authenticated user update of own rating - failure - wrong amount of stars."""
    # Test rating value outside valid range
    # the rating
    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="user_456", 
                    station_id="station_bht")
    
    with pytest.raises(InvalidRatingException, match="Rating value must be between 1 and 5."):
        rating_management.handle_update_rating(
            rating=rating,
            rating_value=0,  # Invalid rating value
            comment="Invalid stars",
        )

def test_handle_update_rating_failure_invalid_comment(rating_management):
    """TC 6b: authenticated user update of own rating - failure - comment too long."""
    # Test comment length outside valid range
    # the rating
    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="user_456", 
                    station_id="station_bht")
    long_comment = "x" * 501  # 501 characters

    with pytest.raises(InvalidCommentException, match="Comment is too long, can't be longer than 500 characters."):
        rating_management.handle_update_rating(
            rating=rating,
            rating_value=5,  
            comment=long_comment,# Invalid comment length
        )

def test_handle_delete_rating_success(rating_management, mock_rating_service):
    """TC 7: authenticated user deletion of own rating - success."""
    # Stub the delete_rating method
    mock_rating_service.delete_rating.return_value = True

# the rating
    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="user_456", 
                    station_id="station_bht")
    
    result = rating_management.handle_delete_rating(
        rating=rating
    )

    assert result is True
    mock_rating_service.delete_rating.assert_called_once_with(
        user_id="user_456",
        station_id="station_bht"
    )

def test_handle_delete_rating_failure_other_users_rating(rating_management):
    """TC 8: authenticated user deletion of other user’s rating - failure."""
    # Simulate a permission error, but again we are not doing that here, it should be checked in the management class
    # mock_rating_service.delete_rating.side_effect = PermissionError("Cannot delete another user's rating.")

    # the rating
    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="other_user", 
                    station_id="station_bht")
    
    with pytest.raises(PermissionError, match="Cannot delete another user's rating."):
        rating_management.handle_delete_rating(
            rating=rating  # Belongs to another user
        )

def test_handle_view_rating_success(rating_management, mock_rating_service):
    """TC 9: authenticated user view rating - success."""
    # the ratings
    rating1 = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="other_user", 
                    station_id="station_bht")
    rating2 = Rating(rating_value=2, 
                    comment="It could have been better.", 
                    user_id="unhappy_user", 
                    station_id="station_bht")
    # Stub the view_ratings method
    mock_rating_service.view_ratings.return_value = [
        rating1,
        rating2,
    ]

    result = rating_management.handle_view_ratings(
        station_id="station_bht",
    )

    assert len(result) == 2
    assert result[0].rating_value == 5
    assert result[0].comment == "What a wonderful experience."
    assert result[0].user_name == "other_user"
    assert result[1].rating_value == 2
    assert result[1].comment == "It could have been better."
    assert result[1].user_name == "unhappy_user"
    assert result[0].station_id == result[1].station_id == "station_bht"
    mock_rating_service.view_ratings.assert_called_once_with(
        station_id="station_bht",
    )

# not sure if this can happen, but should be checked if the exception is propagated correctly
def test_handle_delete_rating_failure_nonexistent_rating(rating_management, mock_rating_service):
    """TC 10: Update Rating - Rating Does Not Exist in the Database."""
    mock_rating_service.delete_rating.side_effect = RatingNotFoundException("Rating not found.")

    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="user_456", 
                    station_id="station_bht")

    with pytest.raises(RatingNotFoundException, match="Rating not found."):
        rating_management.handle_update_rating(
            rating=rating,
            rating_value=3,
            comment="Shit."
        )

def test_handle_delete_rating_failure_nonexistent_rating(rating_management, mock_rating_service):
    """TC 11: Delete Rating - Rating Does Not Exist in the Database."""
    mock_rating_service.delete_rating.side_effect = RatingNotFoundException("Rating not found.")

    rating = Rating(rating_value=5, 
                    comment="What a wonderful experience.", 
                    user_id="user_456", 
                    station_id="station_bht")

    with pytest.raises(RatingNotFoundException, match="Rating not found."):
        rating_management.handle_delete_rating(
            rating=rating
        )

def test_handle_view_rating_failure_station_not_found(rating_management, mock_rating_service):
    """TC 12: View Ratings - Station Does Not Exist."""
    mock_rating_service.view_ratings.side_effect = StationNotFoundException("Station not found.")

    with pytest.raises(ValueError, match="Station not found."):
        rating_management.handle_view_ratings(
            station_id="nonexistent_station",
        )

def test_handle_view_rating_success_empty(rating_management, mock_rating_service):
    """TC 13: authenticated user view rating - success - no ratings to display."""
    # Stub the view_ratings method to return empty list
    mock_rating_service.view_ratings.return_value = []

    result = rating_management.handle_view_ratings(
        station_id="station_bht",
    )

    assert len(result) == 0
    mock_rating_service.view_ratings.assert_called_once_with(
        station_id="station_bht",
    )

def test_handle_create_rating_failure_duplicate_rating(rating_management, mock_rating_service):
    """TC 14: Create Rating - Duplicate Rating."""
    mock_rating_service.create_rating.side_effect = DoubleRatingException("More than one rating for the same station are not allowed.")

    with pytest.raises(DoubleRatingException, match="More than one rating for the same station are not allowed."):
        rating_management.handle_create_rating(
            user_id="user_456",
            station_id="station_123",
            rating_value=4,
            comment="Duplicate rating attempt",
        )
