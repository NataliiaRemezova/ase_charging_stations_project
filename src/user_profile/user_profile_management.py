from dataclasses import dataclass 
from datetime import datetime, time 
from enum import Enum 
from typing import List, Optional

@dataclass(frozen=True)
class Username:
    value: str

    def _post_init_(self):
        if not self._is_valid_username():
            raise InvalidUsernameException(
                "Username muss zwischen 3 und 20 Zeichen lang sein"
            )

def _is_valid_username (self) -> bool:
    return 3 <= len (self.value) <= 20

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