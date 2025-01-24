"""
test_charging_station_management.py

Description:
    This script contains unit tests for the methods of the charging station management in 
    src/charging_station/charging_station_management.py.

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

def test_get_stations_availability():
    # Arrange
    postal_code = "10115"
    repository = MockStationRepository()
    service = StationAvailabilityService(repository)
    # Act
    result = service.get_stations_availability(postal_code)
    # Assert
    assert isinstance(result.event, StationsAvailabilityRequested)
    assert all(isinstance(station.status, StationStatus)
               for station in result.stations)
    assert all(station.postal_code.value == postal_code 
               for station in result.stations)

def test_get_stations_peak_times():
    # Arrange
    station_id = "123"
    service = StationAvailabilityService(MockStationRepository())
    # Act
    result = service.get_station_peak_times(station_id)
    # Assert
    assert isinstance(result.peak_times, list)
    assert all(0 < time.hour < 23 for time in result. peak_times)

def test_invalid_postal_code():
    # Arrange
    service = StationAvailabilityService(MockStationRepository())
    # Act & Assert
    with pytest.raises(InvalidPostalCodeException): 
        service.get_stations_availability("99999") # Keine Berlin PLZ