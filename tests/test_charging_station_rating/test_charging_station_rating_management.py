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

Version:
    Version 0.1
"""

import pytest
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
)

@pytest.fixture
def mock_rating_service(mocker):
    """Fixture to mock the RatingService."""
    mock_service = mocker.patch("charging_station_rating.charging_station_rating_service.RatingService", autospec=True)
    return mock_service.return_value

@pytest.fixture
def rating_management(mock_rating_service):
    """Fixture to initialize RatingManagement with a mocked RatingService."""
    RatingManagement.ratingService = mock_rating_service
    return RatingManagement()

#define the userSession
userSession = {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "user_id": "user_456"
}

def test_handle_create_rating_success(rating_management, mock_rating_service):
    """TC 1: authenticated user creation of valid rating - success."""
    # Stub the create_rating method
    timestamp = datetime.now()
    mock_rating_service.create_rating.return_value = {
        "rating_value": 4,
        "comment": "Great station!",
        "user_id": "user_456",
        "station_id": "station_123",
        "timestamp": timestamp
    }

    result = rating_management.handle_create_rating(
        userSession=userSession,
        user_id="user_456",
        station_id="station_123",
        rating_value=4,
        comment="Great station!",
    )

    assert result.station_id == "station_123"
    assert result.user_id == "user_456"
    assert result.rating_value == 4
    assert result.comment == "Great station!"
    assert result.timestamp == timestamp
    mock_rating_service.create_rating.assert_called_once()

def test_handle_create_rating_failure_invalid_stars(rating_management):
    """TC 2a: authenticated user creation of rating - failure - wrong amount of stars."""
    # Test rating value outside valid range
    with pytest.raises(InvalidRatingException, match="Rating must be between 1 and 5."):
        rating_management.handle_create_rating(
            userSession=userSession,
            user_id="user_456",
            station_id="station_123",
            rating_value=6,
            comment="Invalid stars",
        )

def test_handle_create_rating_failure_invalid_stars(rating_management):
    """TC 2b: authenticated user creation of rating - failure - wrong length of comment."""
    # Test comment length outside valid range
    long_comment = "x" * 501  # 501 characters
    with pytest.raises(InvalidCommentException, match="Comment is too long, can't be longer than 500 characters."):
        rating_management.handle_create_rating(
            userSession=userSession,
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment=long_comment,
        )
    


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
        userSession=userSession,
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
            userSession=userSession,
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
            userSession=userSession,
            rating=rating,
            rating_value=0,  # Invalid rating value
            comment="Invalid stars",
        )

def test_handle_update_rating_failure_invalid_stars(rating_management):
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
            userSession=userSession,
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
        userSession=userSession,
        rating=rating
    )

    assert result is True
    mock_rating_service.delete_rating.assert_called_once_with(
        userSession=userSession,
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
            userSession=userSession,
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
        userSession=userSession,
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
        userSession=userSession,
        station_id="station_bht",
    )

# created by chatGPT from here, need to be checked and changed

def test_handle_delete_rating_failure_nonexistent_rating(rating_management, mock_rating_service):
    """TC 12: Delete Rating - Rating Does Not Exist."""
    mock_rating_service.delete_rating.side_effect = ValueError("Rating not found.")

    with pytest.raises(ValueError, match="Rating not found."):
        rating_management.handle_delete_rating(
            userSession=userSession,
            user_id="user_456",
            rating_id="nonexistent_rating",
        )

def test_handle_view_rating_failure_station_not_found(rating_management, mock_rating_service):
    """TC 13: View Ratings - Station Does Not Exist."""
    mock_rating_service.view_ratings.side_effect = ValueError("Station not found.")

    with pytest.raises(ValueError, match="Station not found."):
        rating_management.handle_view_ratings(
            userSession=userSession,
            station_id="nonexistent_station",
        )

def test_handle_create_rating_failure_duplicate_rating(rating_management, mock_rating_service):
    """TC 14: Create Rating - Duplicate Rating."""
    mock_rating_service.create_rating.side_effect = ValueError("Duplicate rating not allowed.")

    with pytest.raises(ValueError, match="Duplicate rating not allowed."):
        rating_management.handle_create_rating(
            userSession=userSession,
            user_id="user_456",
            station_id="station_123",
            rating_value=4,
            comment="Duplicate rating attempt",
        )

def test_handle_create_rating_failure_invalid_session(rating_management, mock_rating_service):
    """TC 15: Create Rating - Invalid Session."""
    mock_rating_service.create_rating.side_effect = PermissionError("Invalid user session.")

    with pytest.raises(PermissionError, match="Invalid user session."):
        rating_management.handle_create_rating(
            userSession="invalid_session",
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment="Invalid session test",
        )

def test_handle_update_rating_failure_deleted_rating(rating_management, mock_rating_service):
    """TC 16: Update Rating - Rating Deleted."""
    mock_rating_service.update_rating.side_effect = ValueError("Rating has been deleted.")

    with pytest.raises(ValueError, match="Rating has been deleted."):
        rating_management.handle_update_rating(
            userSession=userSession,
            user_id="user_456",
            rating_id="deleted_rating",
            rating_value=5,
            comment="Attempting to update a deleted rating",
        )

def test_handle_view_rating_failure_deleted_user(rating_management, mock_rating_service):
    """TC 17: View Ratings - Deleted User."""
    mock_rating_service.view_ratings.return_value = [
        {"rating_value": 5, "comment": "Good", "user_name": "Deleted User"},
    ]

    result = rating_management.handle_view_ratings(
        userSession=userSession,
        station_id="station_123",
    )

    assert len(result) == 1
    assert result[0]["user_name"] == "Deleted User"
    mock_rating_service.view_ratings.assert_called_once_with(
        userSession=userSession,
        station_id="station_123",
    )

def test_handle_delete_rating_failure_insufficient_permissions(rating_management, mock_rating_service):
    """TC 18: Delete Rating - Insufficient Permissions."""
    mock_rating_service.delete_rating.side_effect = PermissionError("Insufficient permissions.")

    with pytest.raises(PermissionError, match="Insufficient permissions."):
        rating_management.handle_delete_rating(
            userSession=userSession,
            user_id="user_456",
            rating_id="rating_789",
        )

def test_handle_create_rating_failure_missing_comment(rating_management, mock_rating_service):
    """TC 19: Create Rating - Missing Comment."""
    with pytest.raises(ValueError, match="Comment is required."):
        rating_management.handle_create_rating(
            userSession=userSession,
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
            userSession=userSession,
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
            userSession=userSession,
            station_id="invalid_station",
        )

def test_handle_create_rating_failure_too_long_comment(rating_management, mock_rating_service):
    """TC 23: Create Rating - Comment Too Long."""
    with pytest.raises(ValueError, match="Comment exceeds maximum length."):
        rating_management.handle_create_rating(
            userSession=userSession,
            user_id="user_456",
            station_id="station_123",
            rating_value=4,
            comment="A" * 1001,  # Exceeding maximum length
        )

def test_handle_view_rating_failure_no_ratings(rating_management, mock_rating_service):
    """TC 24: View Ratings - No Ratings Found."""
    mock_rating_service.view_ratings.return_value = []

    result = rating_management.handle_view_ratings(
        userSession=userSession,
        station_id="station_123",
    )

    assert result == []
    mock_rating_service.view_ratings.assert_called_once_with(
        userSession=userSession,
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
            userSession=userSession,
            user_id="user_456",
            rating_id="admin_rating",
        )



def test_handle_create_rating_invalid_rating(rating_management):
    """Test creating a rating with an invalid rating value."""
    result = rating_management.handle_create_rating(
        userSession=userSession,
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
        userSession=userSession,
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
            userSession=userSession,
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment="Valid comment",
        )
