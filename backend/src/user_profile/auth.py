from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from datetime import datetime, timedelta
import bcrypt
from backend.db.mongo_client import user_collection
from .user_profile_repositories import UserRepository
from bson.objectid import ObjectId


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
repo = UserRepository(user_collection)

async def verify_password(plain_password: str, hashed_password: str):
    """
    Verify that the provided plain password matches the stored hashed password.
    
    Args:
        plain_password (str): The plaintext password provided by the user.
        hashed_password (str): The hashed password stored in the database.
    
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    try:
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')

        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False
    

async def authenticate_user(username: str, password: str):
    """
    Authenticate the user by verifying their credentials.
    
    Args:
        username (str): The email or username of the user.
        password (str): The plaintext password provided by the user.
    
    Returns:
        dict | bool: The user document if authentication is successful, otherwise False.
    """
    user = await repo.get_user_by_email(username)
    if user is None:
        return False

    if await verify_password(password, user["hashed_password"]):
        return user
    return False

async def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generate a JWT access token with an expiration time.
    
    Args:
        data (dict): The data to encode in the JWT token.
        expires_delta (timedelta, optional): Expiration time delta. Defaults to 15 minutes.
    
    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the currently authenticated user from the JWT token.
    
    Args:
        token (str): The JWT access token provided by the user.
    
    Returns:
        dict: The user document if authentication is successful.
    
    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    