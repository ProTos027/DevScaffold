from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
# Assuming app/models/user.py contains both the SQLAlchemy User model
# and the Pydantic schemas UserProfileResponse and UserProfileUpdate
from app.models.user import User, UserProfileResponse, UserProfileUpdate

# Create the FastAPI router
router = APIRouter(prefix="/users", tags=["User Profile"])

# Placeholder for authentication dependency
# In a real application, this would decode a JWT token, fetch the user from the DB, etc.
# For demonstration, it fetches the first user or creates one if none exists.
def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Dependency to simulate fetching the currently authenticated user.
    In a real application, this would involve actual authentication logic (e.g., JWT).
    For this example, it fetches the first user from the database.
    If no user exists, it creates a dummy user for demonstration purposes.
    """
    user = db.query(User).first()
    if not user:
        # For testing purposes, create a dummy user if none exists.
        # In a real application, this would typically raise an authentication error
        # like: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        try:
            new_user = User(username="testuser", email="test@example.com", hashed_password="dummy_hashed_password")
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except Exception as e:
            # Handle potential unique constraint errors if multiple requests try to create
            # the same dummy user simultaneously during testing.
            # In a real app, this path would not be taken for authentication.
            user = db.query(User).filter(User.username == "testuser").first()
            if user:
                return user
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create dummy user: {e}")
    return user

@router.get("/me", response_model=UserProfileResponse, summary="Fetch current user's profile")
def fetch_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db) # db is not strictly needed here if current_user is already a full ORM object
):
    """
    Retrieves the profile information for the currently authenticated user.
    This endpoint allows a user to view their own details.
    """
    # The 'current_user' object already contains the user's data fetched by get_current_user.
    # It's an SQLAlchemy ORM object, which Pydantic's UserProfileResponse will automatically convert.
    return current_user

@router.put("/me", response_model=UserProfileResponse, summary="Update current user's profile")
def update_user_profile(
    user_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the profile information for the currently authenticated user.
    Fields that are not provided in the request body will not be updated.
    Checks for unique constraints on username and email to prevent conflicts.
    """
    # Check for unique constraints if username or email are updated
    if user_update.username is not None and user_update.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    
    if user_update.email is not None and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Update fields from the Pydantic model
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user) # Add to session (even if it's already there, it marks it as dirty)
    db.commit()
    db.refresh(current_user) # Refresh to get any database-generated values or updated state
    return current_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Delete current user's profile")
def delete_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes the profile of the currently authenticated user.
    This action is irreversible and will permanently remove the user's data from the system.
    Returns a 204 No Content status upon successful deletion.
    """
    db.delete(current_user)
    db.commit()
    # FastAPI automatically returns 204 No Content for functions that return None
    # when status_code is set to 204.
    return