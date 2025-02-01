from datetime import timedelta
import pytest
import httpx
import pytest_asyncio
from backend.src.user_profile.auth import create_access_token
from httpx import AsyncClient
from bson import ObjectId
from fastapi import status
from backend.main import app
import asyncio
from backend.db.mongo_client import user_collection

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest_asyncio.fixture
async def test_user():
    test_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "testpassword"
    }
    await user_collection.insert_one(test_user_data)
    yield test_user_data


@pytest.fixture(scope="session")
async def test_client():
    """Create an HTTPX AsyncClient for testing.

    This ensures that FastAPI's async endpoints are tested correctly 
    with an asynchronous request client.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_access_token(test_user):
    return await create_access_token(
        data={"sub": str(test_user["_id"])}, expires_delta=timedelta(minutes=30)
    )


@pytest.mark.asyncio
async def test_search_stations(test_client):
    response = await test_client.get("/stations/search/10115")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
@pytest.mark.asyncio
async def test_rate_station(test_client, test_access_token, test_user):
    station_id = "123"
    user_id = str(test_user["_id"])
    url = f"/stations/{station_id}/rate?user_id={user_id}"
    response = await test_client.post(
        url,
        json={"rating_value": 5, "comment": "Great station!"},
        headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

@pytest.mark.asyncio
async def test_update_availability(test_client, test_access_token, test_user):
    station_id = "123"
    user_id = str(test_user["_id"])
    url = f"/stations/{station_id}/availability?user_id={user_id}"
    response = await test_client.post(
        url,
        headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

@pytest.mark.asyncio
async def test_get_station_ratings(test_client):
    response = await test_client.get("/stations/123/ratings")
    assert response.status_code == status.HTTP_200_OK


# @pytest.mark.asyncio
# async def test_get_processed_data(test_client):
#     response = await test_client.get("/data")
#     assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
#     if response.status_code == status.HTTP_200_OK:
#         data = response.json()
#         assert "geodat_plz" in data
#         assert "lstat" in data
#         assert "residents" in data

@pytest.mark.asyncio
async def test_root(test_client):
    response = await test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Charging Station Backend API"}


@pytest.mark.asyncio
async def test_update_non_existing_rating(test_client, test_access_token, test_user):
    rating_id = "6512bd43d9caa6e02c990b0a"
    user_id = str(test_user["_id"])
    response = await test_client.put(
        f"/ratings/{rating_id}?user_id={user_id}",
        json={"rating_value": 4, "comment": "Updated rating!"},
        headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

@pytest.mark.asyncio
async def test_delete_non_existing_rating(test_client, test_access_token, test_user):
    rating_id = "6512bd43d9caa6e02c990b0a"
    user_id = str(test_user["_id"])
    response = await test_client.delete(
        f"/ratings/{rating_id}?user_id={user_id}",
        headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
