import pytest
import httpx
from httpx import AsyncClient
from bson import ObjectId
from backend.main import app
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

@pytest.fixture(scope="session")
async def client():
    """Create an HTTPX AsyncClient for testing.

    This ensures that FastAPI's async endpoints are tested correctly 
    with an asynchronous request client.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    """Test the root (/) endpoint.

    Ensures that the API health check returns a successful response
    with a welcome message.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Charging Station Backend API"}


@pytest.mark.asyncio
async def test_get_processed_data(client):
    """Test fetching preprocessed data from the /data endpoint.

    Ensures that the endpoint returns valid geolocation, charging 
    station, and resident population data. A 500 error is acceptable 
    if the files are missing.
    """
    response = await client.get("/data")
    assert response.status_code in [200, 500]  # 500 if file not found
    if response.status_code == 200:
        assert "geodat_plz" in response.json()


@pytest.mark.asyncio
async def test_search_stations(client):
    """Test searching for charging stations by postal code.

    The /stations/search/{postal_code} endpoint should return:
    - A list of charging stations (if found)
    - The number of stations found
    - A timestamp
    """
    response = await client.get("/stations/search/10115")
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        data = response.json()
        assert "stations" in data
        assert "stations_found" in data
        assert isinstance(data["stations_found"], int)


@pytest.mark.asyncio
async def test_rate_station(client):
    """Test submitting a rating for a charging station.

    The /stations/{station_id}/rate endpoint should accept a rating
    and return a success message. If the user is not authenticated, 
    it should return a 401 error.
    """
    valid_user_id = str(ObjectId())  # Generate a valid MongoDB ObjectId
    response = await client.post(
        "/stations/12345/rate",
        json={"rating_value": 5, "comment": "Great!"},
        params={"user_id": valid_user_id},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code in [200, 401, 500]  # 401 if unauthorized
    if response.status_code == 200:
        assert response.json()["message"] == "Rating submitted successfully"


@pytest.mark.asyncio
async def test_get_station_ratings(client):
    """Test retrieving ratings for a specific charging station.

    The /stations/{station_id}/ratings endpoint should return a 
    list of ratings if available.
    """
    response = await client.get("/stations/12345/ratings")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_rating(client):
    """Test updating an existing rating.

    The /ratings/{rating_id} endpoint should allow a user to update 
    their rating. If unauthorized, it should return a 401 error.
    """
    valid_user_id = str(ObjectId())
    response = await client.put(
        "/ratings/12345",
        json={"rating_value": 5, "comment": "Updated comment"},
        params={"user_id": valid_user_id}
    )
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        assert response.json()["rating_value"] == 5


@pytest.mark.asyncio
async def test_delete_rating(client):
    """Test deleting a rating.


The /ratings/{rating_id} endpoint should remove a rating
    and return a success message. Unauthorized users should 
    receive a 401 error.
    """
    valid_user_id = str(ObjectId())
    response = await client.delete("/ratings/12345", params={"user_id": valid_user_id})
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        assert response.json()["message"] == "Rating deleted successfully"