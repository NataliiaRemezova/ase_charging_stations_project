from user_profile_management import UserProfile, ProfileCreated, Username, Email, ProfileResult
from charging_station.charging_station_management import PostalCode
import uuid
from pymongo import MongoClient

class UserProfileService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = client["mydatabase"]

    def create_profile(self, data: dict) -> ProfileResult:
        if self.repository.exists_by_username(data["username"]):
            raise DuplicateUsernameException(
                f"Username {data['username']} already exists"
            )
        if self.repository.exists_by_email(data["email"]):
            raise DuplicateEmailException(
                f"Email {data['email']} already exists"
            )
        
        profile = UserProfile(
            id=str(uuid.uuid4()),
            username=Username(data["username"] ), 
            email=Email(data["email"]), 
            postal_code=PostalCode(data["postal_code"])
        )

        saved_profile = self.repository.save(profile)
        event = ProfileCreated(
            profile_id=saved_profile.id, 
            username=saved_profile.username.value, 
            email=saved_profile.email.value,
        )

        return ProfileResult(profile, event)

    def get_user_by_id(user_id):
        """Retrieve a user by ID from the database."""
        return db.users.find_one({"_id": user_id})

    def update_user_data(user_id, data):
        """Update a user's data in the database."""
        result = db.users.update_one({"_id": user_id}, {"$set": data})
        return result.modified_count

class DuplicateUsernameException(Exception):
    pass

class DuplicateEmailException(Exception):
    pass
