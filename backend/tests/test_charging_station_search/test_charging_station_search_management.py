import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from backend.src.charging_station_search.charging_station_search_management import (
    PostalCode, InvalidPostalCodeException, ChargingStation, ChargingStationSearched, SearchResult
)
from backend.src.charging_station_search.charging_station_search_service import StationSearchService


pytestmark = pytest.mark.asyncio  # Mark all tests as async


async def test_postal_code_validation():
    """
    Test the validation of postal codes:
    - Valid postal codes should be accepted.
    - Invalid postal codes should raise an InvalidPostalCodeException.
    """
    # Valid postal code
    assert PostalCode("10115")

    # Invalid postal codes
    with pytest.raises(InvalidPostalCodeException):
        PostalCode("20115")  # Invalid for the defined region

    with pytest.raises(InvalidPostalCodeException):
        PostalCode("1011")  # Too short


async def test_search_stations_by_valid_postal_code():
    """
    Test searching charging stations by a valid postal code.
    - The service should return a SearchResult containing stations matching the postal code.
    - The ChargingStationSearched event should reflect the correct number of found stations.
    """
    # Arrange
    postal_code = PostalCode("10115")
    repository_mock = AsyncMock()
    repository_mock.find_by_postal_code.return_value = [
        ChargingStation(id="1", location="City Center", postal_code=postal_code, availability_status=True)
    ]
    service = StationSearchService(repository_mock)

    # Act
    result = await service.search_by_postal_code("10115")

    # Assert
    assert isinstance(result, SearchResult)
    assert isinstance(result.event, ChargingStationSearched)
    assert result.event.postal_code == "10115"
    assert result.event.stations_found == 1
    assert len(result.stations) == 1
    assert result.stations[0].postal_code == postal_code


async def test_search_stations_with_invalid_postal_code():
    """
    Test searching charging stations with an invalid postal code.
    - The service should raise an InvalidPostalCodeException.
    """
    # Act & Assert
    with pytest.raises(InvalidPostalCodeException) as exc_info:
        await StationSearchService(AsyncMock()).search_by_postal_code("99999")  # Invalid Berlin PLZ

    assert "99999 ist keine gültige Berliner PLZ" in str(exc_info.value)


async def test_empty_search_result():
    """
    Test searching for charging stations when no stations are found.
    - The service should return a SearchResult with an empty station list.
    - The event should indicate zero stations found.
    """
    # Arrange
    postal_code = PostalCode("10115")
    repository_mock = AsyncMock()
    repository_mock.find_by_postal_code.return_value = []  # No stations found
    service = StationSearchService(repository_mock)

    # Act
    result = await service.search_by_postal_code("10115")

    # Assert
    assert isinstance(result, SearchResult)
    assert result.event.postal_code == "10115"
    assert result.event.stations_found == 0
    assert result.stations == []


async def test_search_stations_availability():
    """
    Test searching for charging stations and checking availability.
    - The service should return all charging stations for a valid postal code.
    - The result should contain stations with both available and unavailable statuses.
    """
    # Arrange
    postal_code = PostalCode("10115")
    repository_mock = AsyncMock()
    repository_mock.find_by_postal_code.return_value = [
        ChargingStation(id="1", location="Station A", postal_code=postal_code, availability_status=True),
        ChargingStation(id="2", location="Station B", postal_code=postal_code, availability_status=False),
    ]
    service = StationSearchService(repository_mock)

    # Act
    result = await service.search_by_postal_code("10115")

    # Assert
    assert isinstance(result, SearchResult)
    assert result.event.postal_code == "10115"
    assert result.event.stations_found == 2
    assert len(result.stations) == 2
    assert any(station.availability_status for station in result.stations)  # At least one station available
    assert any(not station.availability_status for station in result.stations)  # At least one unavailable


async def test_search_invalid_postal_code_format():
    """
    Test searching charging stations with a postal code that has an invalid format.
    - A non-numeric postal code should raise an InvalidPostalCodeException.
    """
    # Act & Assert
    with pytest.raises(InvalidPostalCodeException):
        PostalCode("ABCDE")  # Non-numeric postal code


async def test_search_stations_with_exact_timestamp():
    """
    Test that the search event timestamp is set correctly.
    """
    # Arrange
    postal_code = PostalCode("10115")
    repository_mock = AsyncMock()
    repository_mock.find_by_postal_code.return_value = [
        ChargingStation(id="1", location="City Center", postal_code=postal_code, availability_status=True)
    ]
    service = StationSearchService(repository_mock)

    # Act
    result = await service.search_by_postal_code("10115")

    # Assert
    assert isinstance(result, SearchResult)
    assert isinstance(result.event, ChargingStationSearched)
    assert isinstance(result.event.timestamp, datetime)
    assert abs((result.event.timestamp - datetime.now()).total_seconds()) < 5  # Timestamp should be recent

async def test_postal_code_edge_cases():
    """
    Test edge cases for PostalCode validation.
    - Postal codes with correct prefixes but incorrect length should fail.
    """
    with pytest.raises(InvalidPostalCodeException):
        PostalCode("10")  # Too short, should be 5 digits

    with pytest.raises(InvalidPostalCodeException):
        PostalCode("120000")  # Too long, should be 5 digits

    with pytest.raises(InvalidPostalCodeException):
        PostalCode("abcd1")  # Contains non-numeric characters

    with pytest.raises(InvalidPostalCodeException):
        PostalCode("101150")  # Valid Berlin prefix, but too many digits
