import pytest
from httpx import AsyncClient
import pytest_asyncio
import asyncio
from fastapi import status
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.mongo_client import user_collection
from backend.src.user_profile.auth import create_access_token
from datetime import timedelta
import random
import string


def generate_random_string(length=60):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


@pytest_asyncio.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_email():
    return f"{generate_random_string()}@example.com"

@pytest_asyncio.fixture
async def test_user():
    test_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }
    await user_collection.insert_one(test_user_data)
    yield test_user_data


@pytest_asyncio.fixture
async def test_access_token(test_user):
    return await create_access_token(
        data={"sub": str(test_user["_id"])}, expires_delta=timedelta(minutes=30)
    )


@pytest.mark.asyncio
async def test_register_user(test_client, test_email):
    
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": test_email,
            "password": "testpassword"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "User registered successfully"


@pytest.mark.asyncio
async def test_register_existing_user(test_client, test_email):
    
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": test_email,
            "password": "testpassword"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User already exists"


@pytest.mark.asyncio
async def test_login_user(test_client, test_email):
    
    response = await test_client.post(
        "/auth/token",
        data={"username": test_email, "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_user(test_client):
    
    response = await test_client.post(
        "/auth/token",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_get_user_profile(test_client, test_access_token):
    
    headers = {"Authorization": f"Bearer {test_access_token}"}
    response = await test_client.get("/auth/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.json()
    assert "email" in response.json()


@pytest.mark.asyncio
async def test_get_user_profile_unauthenticated(test_client):
    
    response = await test_client.get("/auth/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_user(test_client, test_access_token, test_user):
    headers = {"Authorization": f"Bearer {test_access_token}"}
    updated_data = {"username": "updateduser"}

    response = await test_client.put(
        f"/auth/users/{test_user['_id']}",
        json=updated_data,
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User updated successfully"


@pytest.mark.asyncio
async def test_update_user_unauthorized(test_client, test_user):
    updated_data = {"username": "unauthorizedupdate"}

    response = await test_client.put(
        f"/auth/users/{test_user['_id']}",
        json=updated_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_other_user_forbidden(test_client, test_access_token):

    headers = {"Authorization": f"Bearer {test_access_token}"}
    updated_data = {"username": "hacker"}

    fake_user_id = "65f2c3f8b35e0c7d6a10e9f1"

    response = await test_client.put(
        f"/auth/users/{fake_user_id}",
        json=updated_data,
        headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to update this user"


@pytest.mark.asyncio
async def test_delete_user(test_client, test_access_token, test_user):
    headers = {"Authorization": f"Bearer {test_access_token}"}

    response = await test_client.delete(
        f"/auth/users/{test_user['_id']}",
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User deleted successfully"


@pytest.mark.asyncio
async def test_delete_user_unauthorized(test_client, test_user):
    response = await test_client.delete(f"/auth/users/{test_user['_id']}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_other_user_forbidden(test_client, test_access_token):
    headers = {"Authorization": f"Bearer {test_access_token}"}
    fake_user_id = "65f2c3f8b35e0c7d6a10e9f2"

    response = await test_client.delete(
        f"/auth/users/{fake_user_id}",
        headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to delete this user"
