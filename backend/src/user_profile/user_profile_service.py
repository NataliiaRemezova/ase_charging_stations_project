from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from .auth import authenticate_user, create_access_token, get_current_active_user
from .models import Token, UserLogin, User

router = APIRouter()

# Dependency Injection
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token Route
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserLogin):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Protected Route
@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
