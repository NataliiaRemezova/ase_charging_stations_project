

class UserProfileService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_profile(self, data: dict) -> ProfileResult:
        if self.repository.exists_by_username(data["username"]):
            raise DuplicateUsernameException(
                f"Username {data['username']} already exists"
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
