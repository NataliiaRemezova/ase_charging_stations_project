"""
test_charging_station_rating_management.py

Description:
    This script contains unit tests for the methods of the charging station rating management in 
    src/charging_station_rating/charging_station_rating_management.py.

Usage:
    It is run with all the other tests in this repo by running 'pytest' in the terminal.

Dependencies:
    pytest

Author:
    Nina Immenroth

Date:
    2024-12-26
    updated for async functions 2025-01-30

Version:
    Version 0.2
"""

import pytest
#import pytest_asyncio
#import asyncio
from unittest.mock import patch, AsyncMock
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

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def mock_rating_service(mocker):
    """Fixture to mock the RatingService with async support."""
    # Patch the target service
    mock_service = AsyncMock()
    mocker.patch(
        "charging_station_rating.charging_station_rating_service.RatingService",
        side_effect = mock_service
    )

    return mock_service

@pytest_asyncio.fixture
async def rating_management(mock_rating_service):
    """Fixture to initialize RatingManagement with a mocked RatingService."""
    # Assuming RatingManagement expects an instance of RatingService in its constructor
    return RatingManagement(ratingService=mock_rating_service)

pytestmark = pytest.mark.asyncio  # Mark all tests as async

@pytest.mark.asyncio
async def test_handle_create_rating_success(mocker, rating_management, mock_rating_service):
    """TC 1: authenticated user creation of valid rating - success."""
    # Stub the create_rating method
    timestamp = datetime.now().utcnow().isoformat()

    mock_rating_service.return_value.create_rating.return_value = {
        "station_id": "station_123",
        "username": "Hansi",
        "user_id": "user_456",
        "rating_value": 4,
        "comment": "Great station!",
        "timestamp": timestamp
    }

    result = await rating_management.handle_create_rating(
        username = "Hansi",
        user_id="user_456",
        station_id="station_123",
        rating_value=4,
        comment="Great station!",
    )

    assert result["station_id"] == "station_123"
    assert result["user_id"] == "user_456"
    assert result["rating_value"] == 4
    assert result["comment"] == "Great station!"
    assert datetime.fromisoformat(result["timestamp"]).replace(microsecond=0) == datetime.fromisoformat(timestamp).replace(microsecond=0)
    mock_rating_service.create_rating.assert_awaited_once()

async def test_handle_create_rating_success(rating_management):
    """TC 1: authenticated user creation of valid rating - success."""
    
    result = await rating_management.handle_create_rating(
        username = "Hansi",
        user_id="user_456",
        station_id="station_123",
        rating_value=4,
        comment="Great station!",
    )

    assert result["station_id"] == "station_123"
    assert result["user_id"] == "user_456"
    assert result["rating_value"] == 4
    assert result["comment"] == "Great station!"
    
def test_handle_create_rating_failure_invalid_stars(rating_management):
    """TC 2a: authenticated user creation of rating - failure - wrong amount of stars."""
    # Test rating value outside valid range
    with pytest.raises(InvalidRatingException, match="Rating must be between 1 and 5."):
        rating_management.handle_create_rating(
            username="Hansi",
            user_id="user_456",
            station_id="station_123",
            rating_value=6,
            comment="Invalid stars",
        )

def test_handle_create_rating_failure_invalid_comment(rating_management):
    """TC 2b: authenticated user creation of rating - failure - wrong length of comment."""
    # Test comment length outside valid range
    long_comment = "x" * 501  # 501 characters
    with pytest.raises(InvalidCommentException, match="Comment is too long, can't be longer than 500 characters."):
        rating_management.handle_create_rating(
            username="Hansi",
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment=long_comment,
        )
    

@pytest.mark.skip(reason="We are not using userSession in the rating management.")
def test_handle_create_rating_failure_unauthenticated_user(rating_management):
    """TC 3: not authenticated user creation of rating - failure."""
    # Test unauthenticated user, not sure if this should be implemented in management or service. 
    # Maybe this test needs to be moved to the test of service
    with pytest.raises(PermissionError, match="User must be authenticated."):
        rating_management.handle_create_rating(
            userSession=None,  # No session
            user_id="user_456",
            station_id="station_123",
            rating_value=4,
            comment="Unauthenticated user",
        )

def test_handle_update_rating_success(rating_management, mock_rating_service):
    """TC 4: authenticated user update of own rating - success."""
    # Stub the update_rating method
    timestamp = datetime.now()
    mock_rating_service.update_rating.return_value = {
        "rating_value": 4,
        "comment": "Updated rating.",
        "user_id": "user_456",
        "station_id": "station_bht",
        "timestamp": timestamp
    }

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
    mock_rating_service.update_rating.assert_called_once()

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

# Not sure how to test the session expiry and where it should be checked (in management or service), 
# now it is in service according to this test
def test_handle_create_rating_failure_invalid_session(rating_management, mock_rating_service):
    """TC 15: Create Rating - Invalid Session."""
    mock_rating_service.create_rating.side_effect = PermissionError("Invalid user session.")

    with pytest.raises(PermissionError, match="Invalid user session."):
        rating_management.handle_create_rating(
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment="Invalid session test",
        )

def test_handle_view_rating_failure_deleted_user(rating_management, mock_rating_service):
    """TC 17: View Ratings - Deleted User."""
    mock_rating_service.view_ratings.return_value = [
        {"rating_value": 5, "comment": "Good", "user_name": "Deleted User"},
    ]

    result = rating_management.handle_view_ratings(
        station_id="station_123",
    )

    assert len(result) == 1
    assert result[0]["user_name"] == "Deleted User"
    mock_rating_service.view_ratings.assert_called_once_with(
        station_id="station_123",
    )

def test_handle_delete_rating_failure_insufficient_permissions(rating_management, mock_rating_service):
    """TC 18: Delete Rating - Insufficient Permissions."""
    mock_rating_service.delete_rating.side_effect = PermissionError("Insufficient permissions.")

    with pytest.raises(PermissionError, match="Insufficient permissions."):
        rating_management.handle_delete_rating(
            user_id="user_456",
            rating_id="rating_789",
        )

def test_handle_create_rating_failure_missing_comment(rating_management, mock_rating_service):
    """TC 19: Create Rating - Missing Comment."""
    with pytest.raises(ValueError, match="Comment is required."):
        rating_management.handle_create_rating(
            user_id="user_456",
            station_id="station_123",
            rating_value=4,
            comment=None,  # Missing comment
        )

def test_handle_update_rating_failure_no_change(rating_management, mock_rating_service):
    """TC 20: Update Rating - No Change Detected."""
    mock_rating_service.update_rating.side_effect = ValueError("No changes detected in the update request.")

    with pytest.raises(ValueError, match="No changes detected in the update request."):
        rating_management.handle_update_rating(
            user_id="user_456",
            rating_id="rating_789",
            rating_value=4,
            comment="Same comment",  # No change from existing data
        )

def test_handle_delete_rating_failure_invalid_session(rating_management, mock_rating_service):
    """TC 21: Delete Rating - Invalid Session."""
    mock_rating_service.delete_rating.side_effect = PermissionError("Invalid session.")

    with pytest.raises(PermissionError, match="Invalid session."):
        rating_management.handle_delete_rating(
            userSession="invalid_session",
            user_id="user_456",
            rating_id="rating_789",
        )

def test_handle_view_rating_failure_invalid_station(rating_management, mock_rating_service):
    """TC 22: View Ratings - Invalid Station."""
    mock_rating_service.view_ratings.side_effect = ValueError("Invalid station ID.")

    with pytest.raises(ValueError, match="Invalid station ID."):
        rating_management.handle_view_ratings(
            station_id="invalid_station",
        )

def test_handle_create_rating_failure_too_long_comment(rating_management, mock_rating_service):
    """TC 23: Create Rating - Comment Too Long."""
    with pytest.raises(ValueError, match="Comment exceeds maximum length."):
        rating_management.handle_create_rating(
            user_id="user_456",
            station_id="station_123",
            rating_value=4,
            comment="A" * 1001,  # Exceeding maximum length
        )

def test_handle_view_rating_failure_no_ratings(rating_management, mock_rating_service):
    """TC 24: View Ratings - No Ratings Found."""
    mock_rating_service.view_ratings.return_value = []

    result = rating_management.handle_view_ratings(
        station_id="station_123",
    )

    assert result == []
    mock_rating_service.view_ratings.assert_called_once_with(
        station_id="station_123",
    )

def test_handle_update_rating_failure_expired_session(rating_management, mock_rating_service):
    """TC 25: Update Rating - Expired Session."""
    mock_rating_service.update_rating.side_effect = PermissionError("Session has expired.")

    with pytest.raises(PermissionError, match="Session has expired."):
        rating_management.handle_update_rating(
            userSession="expired_session",
            user_id="user_456",
            rating_id="rating_789",
            rating_value=4,
            comment="Updated comment",
        )

def test_handle_delete_rating_failure_rating_assigned_to_admin(rating_management, mock_rating_service):
    """TC 26: Delete Rating - Rating Assigned to Admin."""
    mock_rating_service.delete_rating.side_effect = PermissionError("Cannot delete a rating assigned to an admin.")

    with pytest.raises(PermissionError, match="Cannot delete a rating assigned to an admin."):
        rating_management.handle_delete_rating(
            user_id="user_456",
            rating_id="admin_rating",
        )



def test_handle_create_rating_invalid_rating(rating_management):
    """Test creating a rating with an invalid rating value."""
    result = rating_management.handle_create_rating(
        user_id="user_456",
        station_id="station_123",
        rating_value=6,  # Invalid rating value
        comment="This is a test comment",
    )

    assert result is False  # Expecting failure due to invalid rating


def test_handle_create_rating_invalid_comment(rating_management):
    """Test creating a rating with an overly long comment."""
    long_comment = "x" * 501  # 501 characters
    result = rating_management.handle_create_rating(
        user_id="user_456",
        station_id="station_123",
        rating_value=3,
        comment=long_comment,
    )

    assert result is False  # Expecting failure due to overly long comment


def test_handle_create_rating_service_failure(rating_management, mock_rating_service):
    """Test failure in the RatingService's create_rating method."""
    mock_rating_service.create_rating.side_effect = Exception("Service error")

    with pytest.raises(Exception, match="Service error"):
        rating_management.handle_create_rating(
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment="Valid comment",
        )