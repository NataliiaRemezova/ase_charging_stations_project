from pydantic import BaseModel
from typing import Optional

# User Database Model
class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hashed_password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# User Registration Schema
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


# User Login Schema
class LoginRequest(BaseModel):
    username: str
    password: str
