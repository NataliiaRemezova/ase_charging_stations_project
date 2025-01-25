from fastapi import APIRouter, Depends, HTTPException, status, Form
from datetime import timedelta
from .auth import create_access_token, authenticate_user, get_current_user
from .user_profile_repositories import UserRepository
from backend.db.mongo_client import user_collection
from .user_models import RegisterRequest, Token

router = APIRouter()
repo = UserRepository(user_collection)

@router.post("/token", response_model=Token)
async def login_user(
    username: str = Form(...),
    password: str = Form(...)
):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token_expires = timedelta(minutes=30)
    access_token = await create_access_token(
        data={"sub": str(user["_id"])},  # Ensure _id is stringified
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(register: RegisterRequest):
    """
    Register a new user
    """
    user = await repo.get_user_by_email(register.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    await repo.create_user(register.username, register.email, register.password)
    return {"message": "User registered successfully"}


@router.get("/users/me")
async def get_user_profile(current_user=Depends(get_current_user)):
    """
    Retrieve current user profile
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"]
    }

@router.put("/users/{user_id}")
async def update_user(user_id: str, update_data: dict, current_user=Depends(get_current_user)):
    """
    Update user details.
    """
    if str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    success = await repo.update_user(user_id, update_data)
    if not success:
        raise HTTPException(status_code=400, detail="User update failed")
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    """
    Delete a user by ID.
    """
    if str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    success = await repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="User deletion failed")
    return {"message": "User deleted successfully"}