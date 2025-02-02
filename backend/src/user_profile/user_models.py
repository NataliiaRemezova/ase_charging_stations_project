from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """
    Schema for user data stored in the database.
    
    Attributes:
        username (str): The unique username of the user.
        email (str): The email address of the user.
        full_name (Optional[str]): The full name of the user (default: None).
        disabled (Optional[bool]): Whether the user is disabled (default: None).
        hashed_password (str): The hashed password of the user.
    """
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hashed_password: str


class Token(BaseModel):
    """
    Schema for authentication tokens.
    
    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of token, typically "bearer".
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token payload data.
    
    Attributes:
        username (Optional[str]): The username extracted from the token.
    """
    username: Optional[str] = None


class RegisterRequest(BaseModel):
    """
    Schema for user registration request.
    
    Attributes:
        username (str): The chosen username.
        email (str): The user's email address.
        password (str): The plaintext password to be hashed.
    """
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """
    Schema for user login request.
    
    Attributes:
        username (str): The username of the user attempting to log in.
        password (str): The plaintext password of the user.
    """
    username: str
    password: str
