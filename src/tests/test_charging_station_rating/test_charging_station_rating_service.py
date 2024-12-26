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
from charging_station_rating import Rating
from charging_station import ChargingStation
import pytest


def test_create_charging_station_rating():
  charging_station = ChargingStation()
  assert(ChargingStation.rating) == []