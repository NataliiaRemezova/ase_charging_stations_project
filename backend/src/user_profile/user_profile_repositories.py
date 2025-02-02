from backend.db.mongo_client import user_collection
import bcrypt
from bson.objectid import ObjectId
from datetime import datetime


class UserRepository:
    def __init__(self, collection):
        """
        Initialize the UserRepository with a MongoDB collection.
        
        Args:
            collection: MongoDB collection instance.
        """
        self.collection = collection

    async def create_user(self, username: str, email: str, password: str):
        """
        Create a new user with a hashed password.
        
        Args:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The plaintext password to be hashed and stored.
        
        Returns:
            ObjectId: The ID of the newly created user.
        """
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
        """
        Retrieve a user by their email address.
        
        Args:
            email (str): The email of the user to find.
        
        Returns:
            dict: The user document if found, otherwise None.
        """
        return await self.collection.find_one({"email": email})

    async def get_user_by_id(self, user_id: str):
        """
        Retrieve a user by their unique ID.
        
        Args:
            user_id (str): The unique identifier of the user.
        
        Returns:
            dict: The user document if found, otherwise None.
        """
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user
    
    async def update_user(self, user_id: str, update_data: dict):
        """
        Update user details with provided data.
        
        Args:
            user_id (str): The unique identifier of the user.
            update_data (dict): A dictionary containing fields to update.
        
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_user(self, user_id: str):
        """
        Delete a user by their unique ID.
        
        Args:
            user_id (str): The unique identifier of the user.
        
        Returns:
            bool: True if the user was deleted successfully, False otherwise.
        """
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    