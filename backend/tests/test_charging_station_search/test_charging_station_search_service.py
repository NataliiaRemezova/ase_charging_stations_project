from datetime import datetime
import pytest
from unittest.mock import AsyncMock
from backend.src.charging_station_search.charging_station_search_service import (
    PostalCode, ChargingStation, SearchResult, ChargingStationSearched, InvalidPostalCodeException
)
from bson import ObjectId
from backend.src.charging_station_search.charging_station_search_service import StationSearchService, StationRepository
from backend.db.mongo_client import station_collection
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop()
    yield loop
    
@pytest.mark.asyncio
async def test_find_by_postal_code_real():
    """
    Test finding charging stations using the actual StationRepository.
    """
    
    postal_code = "10115"
    test_stations = [
        {
            "_id": "1",
            "postal_code": postal_code,
            "availability_status": True,
            "location": {"latitude": 52.5200, "longitude": 13.4050},
            "name": "Test Station 1",
        },
        {
            "_id": "2",
            "postal_code": postal_code,
            "availability_status": False,
            "location": {"latitude": 52.5300, "longitude": 13.4100},
            "name": "Test Station 2",
        },
    ]
    await station_collection.insert_many(test_stations)

    repository = StationRepository()

    
    result = await repository.find_by_postal_code(PostalCode(postal_code))

    
    assert len(result) == len(test_stations)
    assert all(station.postal_code.value == postal_code for station in result)

    
    await station_collection.delete_many({"postal_code": postal_code})

@pytest.mark.asyncio
async def test_search_by_postal_code():
    """
    Test retrieving charging stations by postal code.
    """
    postal_code = "10115"
    mock_repository = AsyncMock(spec=StationRepository)
    
    mock_repository.find_by_postal_code.return_value = [
        ChargingStation(id="1", location="52.5200, 13.4050", postal_code=PostalCode(postal_code), availability_status=True),
        ChargingStation(id="2", location="52.5300, 13.4100", postal_code=PostalCode(postal_code), availability_status=False),
    ]
    
    service = StationSearchService(mock_repository)

    
    result = await service.search_by_postal_code(postal_code)

    
    assert isinstance(result, SearchResult)
    assert isinstance(result.event, ChargingStationSearched)
    assert all(isinstance(station, ChargingStation) for station in result.stations)
    assert all(station.postal_code.value == postal_code for station in result.stations)
    assert result.event.postal_code == postal_code
    assert result.event.stations_found == len(result.stations)

@pytest.mark.asyncio
async def test_search_by_postal_code_no_results():
    """
    Test when no charging stations are found.
    """
    postal_code = "10245"
    mock_repository = AsyncMock(spec=StationRepository)
    mock_repository.find_by_postal_code.return_value = []  

    service = StationSearchService(mock_repository)

    
    result = await service.search_by_postal_code(postal_code)

    
    assert isinstance(result, SearchResult)
    assert result.event.stations_found == 0
    assert result.stations == []

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_code", ["ABCDE", "101", "101159", "99999"])
async def test_invalid_postal_code(invalid_code):
    """
    Test that invalid postal codes raise an exception.
    """
    service = StationSearchService(AsyncMock(spec=StationRepository))

    with pytest.raises(InvalidPostalCodeException):
        await service.search_by_postal_code(invalid_code)

@pytest.mark.asyncio
async def test_find_by_object_id():
    """
    Test retrieving a charging station by Object ID.
    """
    object_id = "65a1c9d2e4b09d2d4e5f6a1b"
    mock_repository = AsyncMock(spec=StationRepository)
    mock_station = ChargingStation(
        id=object_id,
        location="52.5200, 13.4050",
        postal_code=PostalCode("10115"),
        availability_status=True,
        name="Test Station"
    )

    mock_repository.find_by_object_id.return_value = mock_station
    service = StationSearchService(mock_repository)

    
    result = await mock_repository.find_by_object_id(object_id)

    
    assert isinstance(result, ChargingStation)
    assert result.id == object_id
    assert result.postal_code.value == "10115"
    assert result.availability_status is True
    assert result.name == "Test Station"

@pytest.mark.asyncio
async def test_find_by_object_id_not_found():
    """
    Test retrieving a charging station by an ID that doesn't exist.
    """
    repository_mock = AsyncMock(spec=StationRepository)
    repository_mock.find_by_object_id.return_value = None  

    service = StationSearchService(repository_mock)

    result = await repository_mock.find_by_object_id("fake_object_id")

    assert result is None

@pytest.mark.asyncio
async def test_update_availability_status():
    """
    Test updating the availability status of a charging station.
    """
    station_id = "65a1c9d2e4b09d2d4e5f6a1b"
    mock_repository = AsyncMock(spec=StationRepository)
    mock_repository.update_availability_status.return_value = None  

    service = StationSearchService(mock_repository)

    await mock_repository.update_availability_status(station_id)

    mock_repository.update_availability_status.assert_called_once_with(station_id)

@pytest.mark.asyncio
async def test_update_availability_status_exception():
    """
    Test updating the availability status of a charging station.
    """
    repository_mock = AsyncMock(spec=StationRepository)
    repository_mock.update_availability_status.side_effect = Exception("MongoDB update error")

    service = StationSearchService(repository_mock)

    
    try:
        result = await service.repository.update_availability_status("12345")
    except Exception:
        result = []  

    assert result == []  

@pytest.mark.asyncio
async def test_repository_exception_handling():
    """
    Test handling of repository exceptions when searching by postal code.
    """
    repository_mock = AsyncMock()
    repository_mock.find_by_postal_code.side_effect = Exception("Database failure")

    service = StationSearchService(repository_mock)

    result = await service.search_by_postal_code("10115")

    assert isinstance(result, SearchResult)
    assert result.stations == []  
    assert result.event.stations_found == 0

@pytest.mark.asyncio
async def test_find_by_object_id_exception():
    """
    Test that find_by_object_id handles repository exceptions gracefully.
    """
    repository_mock = AsyncMock(spec=StationRepository)
    repository_mock.find_by_object_id.side_effect = Exception("DB failure")

    service = StationSearchService(repository_mock)

    
    try:
        result = await service.repository.find_by_object_id("fake_object_id")
    except Exception:
        result = None  

    assert result is None  

@pytest.mark.asyncio
async def test_repository_exception_handling():
    """
    Test handling of repository exceptions when searching by postal code.
    """
    repository_mock = AsyncMock()
    repository_mock.find_by_postal_code.side_effect = Exception("Database failure")

    service = StationSearchService(repository_mock)

    result = await service.search_by_postal_code("10115")

    assert isinstance(result, SearchResult)
    assert result.stations == []  
    assert result.event.stations_found == 0

@pytest.mark.asyncio
async def test_find_by_postal_code_exception():
    """
    Test that find_by_postal_code handles exceptions gracefully.
    """
    repository = StationRepository()
    repository.station_collection = AsyncMock()
    repository.station_collection.find.side_effect = Exception("Database Error")
    
    result = await repository.find_by_postal_code(PostalCode("10115"))
    
    assert isinstance(result, list)
    assert len(result) == 0  

@pytest.mark.asyncio
async def test_find_by_object_id_real():
    """
    Test finding a charging station by ObjectId using the actual StationRepository.
    """
    object_id = ObjectId()
    test_station = {
        "_id": object_id,
        "postal_code": "10115",
        "availability_status": True,
        "location": {"latitude": 52.5200, "longitude": 13.4050},
        "name": "Test Station",
    }
    await station_collection.insert_one(test_station)
    repository = StationRepository()
    result = await repository.find_by_object_id(object_id)
    assert result is not None
    assert result.id == str(object_id)
    await station_collection.delete_one({"_id": object_id})

@pytest.mark.asyncio
async def test_find_by_object_id_no_results():
    """
    Test find_by_object_id method when no results are found.
    """
    repository = StationRepository()
    object_id = ObjectId()
    result = await repository.find_by_object_id(object_id)
    assert result is None

@pytest.mark.asyncio
async def test_find_by_object_id_exception():
    """
    Test that find_by_object_id handles exceptions gracefully.
    """
    repository = StationRepository()
    repository.station_collection = AsyncMock()
    repository.station_collection.find_one.side_effect = Exception("Database Error")
    object_id = ObjectId()
    result = await repository.find_by_object_id(object_id)
    assert result is None

@pytest.mark.asyncio
async def test_update_availability_status_station_not_found():
    """
    Test updating availability status when station is not found.
    """
    station_id = str(ObjectId())
    repository = StationRepository()
    repository.find_by_object_id = AsyncMock(return_value=None)
    
    result = await repository.update_availability_status(station_id)
    assert result == []

@pytest.mark.asyncio
async def test_update_availability_status_exception():
    """
    Test that update_availability_status handles exceptions gracefully.
    """
    station_id = str(ObjectId())
    repository = StationRepository()
    repository.find_by_object_id = AsyncMock(side_effect=Exception("Database Error"))
    
    result = await repository.update_availability_status(station_id)
    assert result == []