from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict

# --- Data Models ---

class UserBase(BaseModel):
    """
    Base model for user data, containing common fields.
    """
    username: str = Field(..., example="john_doe", description="Unique username of the user")
    email: str = Field(..., example="john.doe@example.com", description="Email address of the user")
    full_name: Optional[str] = Field(None, example="John Doe", description="Full name of the user")

class User(UserBase):
    """
    Represents a full user profile in the system, including the ID.
    This model is used for internal representation and as a base for responses.
    """
    id: int = Field(..., example=1, description="Unique identifier for the user")

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with ORM objects if used

class UserResponse(User):
    """
    Response model for user profile data. Inherits from User.
    Can be extended if specific response-only fields are needed.
    """
    pass

class UserUpdate(BaseModel):
    """
    Request model for updating user profile data.
    All fields are optional, allowing for partial updates.
    """
    email: Optional[str] = Field(None, example="new.email@example.com", description="New email address for the user")
    full_name: Optional[str] = Field(None, example="New full name for the user")

# --- Service Layer (Mock) ---

class UserProfileService:
    """
    A service class to handle user profile operations.
    This class simulates interactions with a database or external API.
    """
    def __init__(self):
        # Simulate a database with some initial user data
        self.db: Dict[int, User] = {
            1: User(id=1, username="testuser", email="test@example.com", full_name="Test User")
        }

    def get_user_profile(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user profile by their ID.
        """
        return self.db.get(user_id)

    def update_user_profile(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Updates an existing user profile with the provided data.
        """
        user = self.db.get(user_id)
        if user:
            # Convert Pydantic model to dictionary, excluding fields that were not set
            update_data = user_data.dict(exclude_unset=True)
            # Update user attributes
            for key, value in update_data.items():
                setattr(user, key, value)
            self.db[user_id] = user  # "Save" the updated user back to the "database"
            return user
        return None

# --- Dependencies ---

def get_user_service() -> UserProfileService:
    """
    Dependency that provides an instance of UserProfileService.
    In a real application, this might manage database sessions or connections.
    """
    return UserProfileService()

def get_current_user() -> User:
    """
    Dependency to simulate an authenticated user.
    In a real application, this would typically involve:
    1. Extracting a token (e.g., JWT) from the request header.
    2. Validating the token.
    3. Decoding the token to get the user ID.
    4. Fetching the user from the database based on the ID.
    For this example, we hardcode a mock authenticated user with ID 1.
    """
    # Simulate an authenticated user with ID 1
    mock_user = User(id=1, username="authenticated_user", email="auth@example.com", full_name="Authenticated User")
    return mock_user

# --- APIRouter Definition ---

router = APIRouter(
    prefix="/users",
    tags=["User Profile"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=UserResponse)
async def get_authenticated_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserProfileService = Depends(get_user_service)
) -> UserResponse:
    """
    Retrieve the profile of the currently authenticated user.

    This endpoint fetches the detailed profile information for the user
    who is currently authenticated.

    Raises:
        HTTPException: 404 Not Found if the user profile cannot be retrieved
                       (though this should ideally not happen for an authenticated user).
    """
    user_profile = user_service.get_user_profile(current_user.id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found for the authenticated user."
        )
    return user_profile

@router.put("/me", response_model=UserResponse)
async def update_authenticated_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserProfileService = Depends(get_user_service)
) -> UserResponse:
    """
    Update the profile of the currently authenticated user.

    This endpoint allows the authenticated user to update their profile details,
    such as email or full name. Partial updates are supported.

    Args:
        user_update (UserUpdate): The data to update the user profile with.
                                  Fields not provided will remain unchanged.

    Raises:
        HTTPException: 404 Not Found if the user profile cannot be found.
        HTTPException: 422 Unprocessable Entity if the input data is invalid.
    """
    updated_user = user_service.update_user_profile(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found for the authenticated user."
        )
    return updated_user