import pytest
from user_profile import ProfileCreated, ProfileDeleted, ProfileStatus, UserProfileService, DuplicateUsernameException, UserRepository

def test_create_valid_user_profile():
    # Arrange
    profile_data = {
        "username": "berlin_user",
        "email": "test@example.com",
        "postal_code": "10115"
    }
    service = UserProfileService(UserRepository())
    # Act
    result = service.create_profile(profile_data)
    # Assert
    assert isinstance(result.event, ProfileCreated)
    assert result.profile.username == profile_data["username"]
    assert result.profile.status == ProfileStatus.ACTIVE

def test_duplicate_username():
    # Arrange
    service = UserProfileService(UserRepository())
    existing_profile = {
        "username": "existing_user",
        "email": "test@example.com",
        "postal_code": "10115"
    }
    service.create_profile(existing_profile)
    # Act & Assert
    with pytest.raises(DuplicateUsernameException):
        service.create_profile(existing_profile)

def test_delete_profile():
    # Arrange
    service = UserProfileService (UserRepository())
    profile_id = "user_123"
    # Act
    result = service.delete_profile(profile_id)
    # Assert
    assert isinstance(result.event, ProfileDeleted)
    assert result.event.profile_id == profile_id