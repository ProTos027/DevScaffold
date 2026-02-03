from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Optional

# --- Data Models ---

class UserBase(BaseModel):
    """Base model for user profile data."""
    name: str = Field(..., example="John Doe", min_length=1)
    email: str = Field(..., example="john.doe@example.com", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class UserUpdate(UserBase):
    """Model for updating an existing user profile."""
    name: Optional[str] = Field(None, example="Jane Doe", min_length=1)
    email: Optional[str] = Field(None, example="jane.doe@example.com", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class User(UserBase):
    """Model representing a complete user profile, including its ID."""
    id: int = Field(..., example=1, ge=1)

    class Config:
        orm_mode = True  # Enable compatibility with ORM models (e.g., SQLAlchemy)

# --- Service Layer (Dependency) ---

class UserProfileService:
    """
    A service class responsible for handling user profile operations.
    This class simulates a persistent data store using an in-memory dictionary.
    In a real application, this would interact with a database.
    """
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1

    def create_user_profile(self, user_data: UserBase) -> User:
        """
        Creates a new user profile and assigns a unique ID.
        Although not exposed via a public interface in this router,
        this method demonstrates the internal responsibility.
        """
        user_id = self._next_id
        self._next_id += 1
        user = User(id=user_id, **user_data.dict())
        self._users[user_id] = user
        return user

    def retrieve_user_profile(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user profile by its unique identifier.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User object if found, otherwise None.
        """
        return self._users.get(user_id)

    def update_user_profile(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Updates an existing user profile with the provided data.

        Args:
            user_id: The ID of the user to update.
            user_data: The UserUpdate model containing the fields to update.

        Returns:
            The updated User object if found, otherwise None.
        """
        if user_id not in self._users:
            return None
        existing_user = self._users[user_id]
        update_data = user_data.dict(exclude_unset=True)  # Only update fields that are explicitly set
        updated_user = existing_user.copy(update=update_data)
        self._users[user_id] = updated_user
        return updated_user

    def delete_user_profile(self, user_id: int) -> bool:
        """
        Deletes a user profile by its unique identifier.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if the user was deleted, False if not found.
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

# Global instance of the service for dependency injection
# In a real application, this might be managed by a DI container or a database session.
_user_profile_service_instance = UserProfileService()
# Populate with some initial data for demonstration
_user_profile_service_instance.create_user_profile(UserBase(name="Alice Smith", email="alice@example.com"))
_user_profile_service_instance.create_user_profile(UserBase(name="Bob Johnson", email="bob@example.com"))


def get_user_profile_service() -> UserProfileService:
    """
    Dependency injector that provides a UserProfileService instance.
    This ensures the same service instance (and thus the same in-memory data)
    is used across requests for demonstration purposes.
    """
    return _user_profile_service_instance

# --- FastAPI Router ---

router = APIRouter(
    prefix="/users",
    tags=["User Profiles"],
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation Error"}
    },
)

@router.get(
    "/{user_id}",
    response_model=User,
    summary="Retrieve a user profile",
    status_code=status.HTTP_200_OK,
)
async def retrieve_user_profile_endpoint(
    user_id: int = Field(..., ge=1, description="The unique identifier of the user"),
    service: UserProfileService = Depends(get_user_profile_service),
) -> User:
    """
    Retrieves a single user profile by their unique ID.

    This endpoint allows clients to fetch detailed information about a specific user.
    If the user with the given ID does not exist, a 404 Not Found error is returned.

    - **user_id**: The unique integer ID of the user to retrieve.
    """
    user = service.retrieve_user_profile(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put(
    "/{user_id}",
    response_model=User,
    summary="Update an existing user profile",
    status_code=status.HTTP_200_OK,
)
async def update_user_profile_endpoint(
    user_id: int = Field(..., ge=1, description="The unique identifier of the user to update"),
    user_data: UserUpdate = Depends(),
    service: UserProfileService = Depends(get_user_profile_service),
) -> User:
    """
    Updates an existing user profile with the provided data.

    This endpoint allows clients to modify an existing user's details.
    Only the fields provided in the request body will be updated.
    If the user with the given ID does not exist, a 404 Not Found error is returned.

    - **user_id**: The unique integer ID of the user to update.
    - **user_data**: The user profile data to update. Fields can be omitted if no change is desired.
    """
    updated_user = service.update_user_profile(user_id, user_data)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user profile",
    response_model=None, # No content is returned for a 204 status
)
async def delete_user_profile_endpoint(
    user_id: int = Field(..., ge=1, description="The unique identifier of the user to delete"),
    service: UserProfileService = Depends(get_user_profile_service),
) -> None:
    """
    Deletes a user profile by their unique ID.

    This endpoint permanently removes a user profile from the system.
    If the user with the given ID does not exist, a 404 Not Found error is returned.
    A successful deletion returns a 204 No Content status.

    - **user_id**: The unique integer ID of the user to delete.
    """
    success = service.delete_user_profile(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None # FastAPI handles 204 No Content for None return