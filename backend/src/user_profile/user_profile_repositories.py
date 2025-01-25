from backend.db.mongo_client import user_collection
import bcrypt
from bson.objectid import ObjectId
from datetime import datetime


class UserRepository:
    def __init__(self, collection):
        self.collection = collection

    async def create_user(self, username: str, email: str, password: str):
        """Create user."""
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
        """Get user by email."""
        return await self.collection.find_one({"email": email})

    async def get_user_by_id(self, user_id: str):
        """Get user by id."""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user
    
    async def update_user(self, user_id: str, update_data: dict):
        """Update user details."""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_user(self, user_id: str):
        """Delete a user by ID."""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    