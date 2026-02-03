import os
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from jose import JWTError, jwt

# --- Configuration (Ideally from environment variables) ---
# In a real application, these should be loaded securely from environment variables.
# For demonstration purposes, default values are provided.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# --- Data Models ---

class UserBase(BaseModel):
    """Base model for user data."""
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(UserBase):
    """Model for user login credentials."""
    password: str

class UserResponse(UserBase):
    """Model for returning user data (excluding sensitive info like password)."""
    id: int = Field(..., example=1)

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for Pydantic v2

class Token(BaseModel):
    """Model for JWT access token response."""
    access_token: str
    token_type: str = "bearer"

# --- Mock Database (In a real application, this would be a proper database) ---
_mock_db: List[dict] = []
_next_user_id = 1

# --- Service Layer ---

class AuthService:
    """
    Service layer responsible for user registration and authentication logic.
    Simulates interactions with a user data store.
    """
    def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Registers a new user in the system.

        Args:
            user_data: The UserCreate object containing username and password.

        Returns:
            A UserResponse object for the newly created user.

        Raises:
            HTTPException: If the username already exists (409 Conflict).
        """
        global _next_user_id
        # Check if user already exists
        if any(u["username"] == user_data.username for u in _mock_db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )

        # In a real application, the password would be hashed securely (e.g., using bcrypt)
        # For this example, we're just storing a placeholder for the hashed password.
        new_user = {
            "id": _next_user_id,
            "username": user_data.username,
            "hashed_password": user_data.password + "_hashed" # Placeholder for hashed password
        }
        _mock_db.append(new_user)
        _next_user_id += 1
        return UserResponse(id=new_user["id"], username=new_user["username"])

    def authenticate_user(self, user_data: UserLogin) -> Optional[UserResponse]:
        """
        Authenticates a user based on their username and password.

        Args:
            user_data: The UserLogin object containing username and password.

        Returns:
            A UserResponse object if authentication is successful, otherwise None.
        """
        for user in _mock_db:
            # In a real application, verify the hashed password (e.g., bcrypt.checkpw)
            if user["username"] == user_data.username and user["hashed_password"] == user_data.password + "_hashed":
                return UserResponse(id=user["id"], username=user["username"])
        return None

# --- JWT Handler ---

class JWTHandler:
    """
    Handles the generation and validation of JSON Web Tokens (JWTs).
    """
    def generate_jwt_token(self, user_id: int) -> str:
        """
        Generates an access token for a given user ID.

        Args:
            user_id: The ID of the user for whom the token is generated.

        Returns:
            A string representing the encoded JWT.
        """
        to_encode = {"user_id": user_id}
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def validate_jwt_token(self, token: str) -> Optional[int]:
        """
        Validates a JWT token and extracts the user ID if the token is valid.

        Args:
            token: The JWT string to validate.

        Returns:
            The user ID (int) if the token is valid and contains a user_id, otherwise None.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("user_id")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None

# --- Dependency Injection ---

def get_auth_service() -> AuthService:
    """Dependency provider for AuthService."""
    return AuthService()

def get_jwt_handler() -> JWTHandler:
    """Dependency provider for JWTHandler."""
    return JWTHandler()

# --- APIRouter Setup ---

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# --- Public Interfaces (Endpoints) ---

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user with a unique username and password. "
                "Returns the created user's ID and username upon successful registration."
)
async def register_user_endpoint(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Registers a new user in the system.

    - **username**: A unique string to identify the user.
    - **password**: The user's chosen password (minimum 6 characters).

    Raises:
        HTTPException:
            - `409 Conflict`: If the provided username is already taken.
            - `500 Internal Server Error`: For unexpected server issues.
    """
    try:
        user = auth_service.register_user(user_data)
        return user
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions from the service layer
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during registration: {e}"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login user and get JWT token",
    description="Authenticates a user with username and password. "
                "Returns an access token if authentication is successful."
)
async def login_user_endpoint(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
    jwt_handler: JWTHandler = Depends(get_jwt_handler)
):
    """
    Authenticates a user and provides an access token.

    - **username**: The user's registered username.
    - **password**: The user's password.

    Raises:
        HTTPException:
            - `401 Unauthorized`: If the username or password is incorrect.
            - `500 Internal Server Error`: For unexpected server issues.
    """
    user = auth_service.authenticate_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        access_token = jwt_handler.generate_jwt_token(user_id=user.id)
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {e}"
        )