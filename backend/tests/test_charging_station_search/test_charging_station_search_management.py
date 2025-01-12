"""
test_charging_station_search_management.py

Description:
    This script contains unit tests for the methods of the charging station search management in 
    src/charging_station_search/charging_station_search_management.py.

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
from dataclasses import dataclass 
from datetime import datetime 
from typing import List, Optional
from charging_station.charging_station_management import PostalCode
from charging_station_search.charging_station_search_management import InvalidPostalCodeException
from charging_station_search.charging_station_search_service import ChargingStationSearchService

def test_berlin_postal_code_validation():
# Arrange & Act & Assert
    assert PostalCode.create("10115") # Valid 
    with pytest.raises(InvalidPostalCodeException):
        PostalCode.create("20115" ) # Hamburg 
    with pytest.raises(InvalidPostalCodeException):
        PostalCode.create("1011") # Zu kurz

def test_find_stations_in_postal_code_area():
    # Arrange
    postal_code = PostalCode.create("10115" )
    service = ChargingStationSearchService()
    # Act
    result = service.search_by_postal_code(postal_code)
    # Assert
    assert result is not None
    assert all(station.is_in_area(postal_code)
               for station in result.stations)
    
def test_search_stations_by_valid_postal_code():
    # Arrange
    postal_code = "10115"
    service = StationSearchService(MockStationRepository())
    # Act
    result = service.search_by_postal_code(postal_code)
    # Assert
    assert isinstance(result.event, ChargingStationSearched)
    assert all(station.postal_code == postal_code
        for station in result.stations)

def test_search_with_invalid_postal_code():
    # Arrange
    service = StationSearchService(MockStationRepository())
    # Act & Assert
    with pytest.raises(InvalidPostalCodeException):
        service.search_by_postal_code("99999") # Ungültige PLZ