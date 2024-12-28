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
    RatingManagement,
    RatingCreated,
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
        userSession="dummy_session",
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


def test_handle_create_rating_invalid_rating(rating_management):
    """Test creating a rating with an invalid rating value."""
    result = rating_management.handle_create_rating(
        userSession="dummy_session",
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
        userSession="dummy_session",
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
            userSession="dummy_session",
            user_id="user_456",
            station_id="station_123",
            rating_value=3,
            comment="Valid comment",
        )
