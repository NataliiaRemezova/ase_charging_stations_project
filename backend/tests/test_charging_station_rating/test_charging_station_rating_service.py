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
    2024-12-26
    updated for async functions 2025-01-30

Version:
    Version 0.2
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from datetime import datetime
from backend.src.charging_station_rating.charging_station_rating_service import (
    RatingService,
    RatingNotFoundException,
    StationNotFoundException
)

@pytest_asyncio.fixture
def mock_repository():
    """
    Create a mock for RatingRepository.
    """
    return AsyncMock()

@pytest_asyncio.fixture
def rating_service(mock_repository):
    """
    Create a RatingService instance with a mocked repository.
    """
    return RatingService(mock_repository)


@pytest.mark.asyncio
async def test_create_rating(rating_service, mock_repository):
    """ TC 1: Test creating a new rating successfully."""
    # Arrange
    mock_repository.save_rating.return_value = "12345"
    rating_data = {
        "station_id": "station_1",
        "username": "test_user",
        "user_id": "user_123",
        "rating_value": 5,
        "comment": "Great station!"
    }

    # Act
    result = await rating_service.create_rating(rating_data)

    # Assert
    assert result["id"] == "12345"
    assert result["station_id"] == "station_1"
    assert result["username"] == "test_user"
    assert result["rating_value"] == 5
    mock_repository.save_rating.assert_awaited_once_with(
        "station_1", "test_user", "user_123", 5, "Great station!"
    )


@pytest.mark.asyncio
async def test_get_ratings_by_station_success(rating_service, mock_repository):
    """ TC 2a: Test retrieving ratings by station - success."""
    # Arrange
    mock_repository.get_ratings_by_station.return_value = [
        {
            "id": "123",
            "rating_value": 5,
            "comment": "Awesome station!",
            "username": "user1",
            "user_id": "user_123",
            "timestamp": datetime.utcnow().isoformat()
        }
    ]

    # Act
    result = await rating_service.get_ratings_by_station("station_1")

    # Assert
    assert len(result) == 1
    assert result[0]["rating_value"] == 5
    mock_repository.get_ratings_by_station.assert_awaited_once_with("station_1")

@pytest.mark.asyncio
async def test_get_ratings_by_station_not_found(rating_service, mock_repository):
    """
    TC 2b: Test retrieving ratings by station - failure.
    """
    # Arrange
    mock_repository.get_ratings_by_station.side_effect = StationNotFoundException("Station not found.")

    # Act & Assert
    with pytest.raises(StationNotFoundException, match="Station not found."):
        await rating_service.get_ratings_by_station("station_1")
    
    mock_repository.get_ratings_by_station.assert_awaited_once_with("station_1")

@pytest.mark.asyncio
async def test_get_rating_by_id_success(rating_service, mock_repository):
    """ TC 3a: Test retrieving a rating by ID - success."""
    # Arrange
    mock_repository.get_rating_by_id.return_value = {
        "rating_value": 4,
        "comment": "Good station!",
        "username": "test_user",
        "user_id": "user_123",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Act
    result = await rating_service.get_rating_by_id("12345")

    # Assert
    assert result["rating_value"] == 4
    assert result["comment"] == "Good station!"
    mock_repository.get_rating_by_id.assert_awaited_once_with("12345")

@pytest.mark.asyncio
async def test_get_rating_by_id_not_found(rating_service, mock_repository):
    """
    TC 3b: Test retrieving a rating by ID - failure.
    """
    # Arrange
    mock_repository.get_rating_by_id.side_effect = RatingNotFoundException("Rating not found.")

    # Act & Assert
    with pytest.raises(RatingNotFoundException, match="Rating not found."):
        await rating_service.get_rating_by_id("12345")

    mock_repository.get_rating_by_id.assert_awaited_once_with("12345")

@pytest.mark.asyncio
async def test_update_rating_success(rating_service, mock_repository):
    """ TC4a: Test updating a rating - success."""
    # Arrange
    mock_repository.update_rating.return_value = True
    mock_repository.get_rating_by_id.return_value = {
        "rating_value": 5,
        "comment": "Updated comment!",
        "username": "user_123",
        "user_id": "user_123",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Act
    result = await rating_service.update_rating("12345", 5, "Updated comment!")

    # Assert
    assert result["rating_value"] == 5
    assert result["comment"] == "Updated comment!"
    mock_repository.update_rating.assert_awaited_once_with("12345", 5, "Updated comment!")


@pytest.mark.asyncio
async def test_update_rating_failure(rating_service, mock_repository):
    """ TC4b: Test updating a rating when the rating is not found - failure."""
    # Arrange
    mock_repository.update_rating.return_value = False

    # Act & Assert
    with pytest.raises(ValueError, match="Rating not found or update failed."):
        await rating_service.update_rating("12345", 4, "New comment")


@pytest.mark.asyncio
async def test_delete_rating_success(rating_service, mock_repository):
    """ TC5a: Test deleting a rating - success."""
    # Arrange
    mock_repository.delete_rating.return_value = True

    # Act
    result = await rating_service.delete_rating("12345")

    # Assert
    assert result is True
    mock_repository.delete_rating.assert_awaited_once_with("12345")


@pytest.mark.asyncio
async def test_delete_rating_failure(rating_service, mock_repository):
    """ TC5b: Test deleting a rating that does not exist - failure.
    """
    # Arrange
    mock_repository.delete_rating.return_value = False

    # Act
    result = await rating_service.delete_rating("12345")

    # Assert
    assert result is False
    mock_repository.delete_rating.assert_awaited_once_with("12345")

