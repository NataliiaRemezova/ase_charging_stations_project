from backend.db.mongo_client import user_collection
import bcrypt
from bson.objectid import ObjectId
from datetime import datetime


class UserRepository:
    def __init__(self, collection):
        self.collection = collection

    async def create_user(self, username: str, email: str, password: str):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
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
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user

    async def verify_user_password(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user["hashed_password"].encode('utf-8')):
            return user
        return None
    