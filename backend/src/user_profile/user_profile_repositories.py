from backend.db.mongo_client import user_collection
from passlib.context import CryptContext
from bson.objectid import ObjectId
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, collection):
        self.collection = collection

    async def create_user(self, username: str, email: str, password: str):
        hashed_password = pwd_context.hash(password)
        user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "date_joined": datetime.utcnow(),
            "profile_picture": None
        }
        result = await self.collection.insert_one(user)
        return result.inserted_id

    async def get_user_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def get_user_by_id(self, user_id: str):
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def verify_user_password(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if user and pwd_context.verify(password, user["hashed_password"]):
            return user
        return None
