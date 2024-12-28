from dataclasses import dataclass, field
from datetime import datetime, time 
from enum import Enum 
from typing import List, Optional, ClassVar
from email_validator import validate_email, EmailNotValidError

from user_profile_service import UserProfileService
from charging_station.charging_station_management import PostalCode

@dataclass(frozen=True)
class Username:
    value: str

    def _post_init_(self):
        if not self._is_valid_username():
            raise InvalidUsernameException(
                "Username must be between 3 and 20 characters."
            )
        
    def _is_valid_username(self) -> bool:
        return 3 <= len(self.value) <= 20

@dataclass(frozen=True)
class Email:
    value: str

    def _post_init_(self):
        if not self._is_valid_email():
            raise InvalidEmailException(
                "Email must be of shape \"prefix@domain.ending\"."
            )

    def _is_valid_email(self) -> bool:
        try:
            # Validate and return the normalized email address
            valid = validate_email(self.value)
            return True
        except EmailNotValidError as e:
            # Print error message if email is invalid
            print(str(e))
            return False

class ProfileStatus(Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

@dataclass 
class UserProfile:
    id: str
    username: Username
    email: Email
    postal_code: PostalCode
    status: ProfileStatus = ProfileStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

@dataclass (frozen=True)
class ProfileCreated:
    profile_id: str 
    username: str
    email: str
    postal_code: str 
    timestamp: datetime

@dataclass (frozen=True)
class ProfileDeleted:
    profile_id: str 
    timestamp: datetime

class UserProfileManagement:
    userService: ClassVar[UserProfileService] = UserProfileService()

    def handle_create_user(self, username, email, postal_code):
        username = Username(username)
        email = Email(email)
        postal_code = PostalCode(postal_code)

        result = self.userService.create_profile()


# Custom exceptions
class InvalidUsernameException(Exception):
    pass

class InvalidEmailException(Exception):
    pass
