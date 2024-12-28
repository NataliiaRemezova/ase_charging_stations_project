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
from charging_station_rating.charging_station_rating_management import Rating, InvalidRatingException
from charging_station_rating.charging_station_rating_service import RatingService
from charging_station.charging_station_management import ChargingStation
import pytest


def test_create_charging_station_rating():
  charging_station = ChargingStation()
  assert(ChargingStation.rating) == []

def test_valid_charging_station_rating():
    # Arrange
    station_id = "123"
    user_id = "456"
    rating_data = {
        "stars": 4,
        "comment": "Sehr gut erreichbar, schnelles Laden",
    }
    service = RatingService(MockRatingRepository())
    # Act
    result = service.submit_rating(station_id, user_id, rating_data)
    # Assert
    assert result.event.type == "RatingCreated"
    assert result.event.rating_value == 4
    assert result.event.station_id == station_id

def test_invalid_rating_value():
    # Arrange
    rating_data = {"stars": 6} # Ungültig: > 5
    service = RatingService(MockRatingRepository())
    # Act & Assert
    with pytest.raises(InvalidRatingException):
        service.submit_rating("123", "456", rating_data)