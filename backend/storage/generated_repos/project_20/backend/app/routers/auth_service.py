import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

# --- Configuration (In a real app, these would be loaded from environment variables or a config file) ---
# For password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# For JWT (mocked for this example)
SECRET_KEY = "your-super-secret-jwt-key"  # Replace with a strong, random key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- Data Models ---
class UserBase(BaseModel):
    """Base model for user data."""
    email: EmailStr


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str


class UserLogin(UserBase):
    """Model for user login credentials."""
    password: str


class UserInDB(UserBase):
    """Model representing a user as stored in the database."""
    id: uuid.UUID
    hashed_password: str

    class Config:
        from_attributes = True  # Enable ORM mode for Pydantic v2


class UserResponse(UserBase):
    """Model for user data returned in responses (without sensitive info)."""
    id: uuid.UUID

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Model for JWT access token response."""
    access_token: str
    token_type: str = "bearer"


# --- Mock Database (In a real app, this would be an actual database connection) ---
fake_users_db: dict[EmailStr, UserInDB] = {}


# --- Auth Service Layer ---
class AuthService:
    """
    Service class encapsulating authentication logic.
    Handles user registration, authentication, password hashing, and token generation.
    """

    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM

    def verify_password_hash(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain-text password against a hashed password.

        Args:
            plain_password: The password provided by the user.
            hashed_password: The stored hashed password.

        Returns:
            True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        """
        Hashes a plain-text password.

        Args:
            password: The plain-text password to hash.

        Returns:
            The hashed password string.
        """
        return self.pwd_context.hash(password)

    def generate_jwt_token(self, user_id: uuid.UUID) -> str:
        """
        Generates a JWT token for a given user ID.

        Note: This is a simplified mock. In a real application, you would use a library
        like `python-jose` to create signed tokens with expiration times.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            A mock JWT token string.
        """
        # In a real app, you'd use `jwt.encode` from `python-jose`
        # import jwt
        # from datetime import datetime, timedelta
        # to_encode = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
        # encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        # return encoded_jwt
        return f"mock_jwt_for_user_{user_id}"

    def register_new_user(self, user_data: UserCreate) -> UserInDB:
        """
        Registers a new user in the system.

        Args:
            user_data: The UserCreate model containing email and password.

        Returns:
            The created UserInDB object.

        Raises:
            ValueError: If a user with the provided email already exists.
        """
        if fake_users_db.get(user_data.email):
            raise ValueError("User with this email already exists")

        hashed_password = self._hash_password(user_data.password)
        new_user = UserInDB(
            id=uuid.uuid4(),
            email=user_data.email,
            hashed_password=hashed_password
        )
        fake_users_db[new_user.email] = new_user
        return new_user

    def authenticate_user_login(self, email: EmailStr, password: str) -> Optional[UserInDB]:
        """
        Authenticates a user's login credentials.

        Args:
            email: The user's email address.
            password: The user's plain-text password.

        Returns:
            The UserInDB object if authentication is successful, None otherwise.
        """
        user = fake_users_db.get(email)
        if not user or not self.verify_password_hash(password, user.hashed_password):
            return None
        return user


# --- Dependency Injection ---
def get_auth_service() -> AuthService:
    """
    Dependency that provides an instance of the AuthService.
    This allows for easy testing and swapping of service implementations.
    """
    return AuthService()


# --- FastAPI Router ---
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with the provided email and password."
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Registers a new user in the system.

    - **email**: The user's email address (must be unique).
    - **password**: The user's chosen password.

    **Returns**:
    - `201 Created`: The ID and email of the newly registered user.

    **Raises**:
    - `409 Conflict`: If a user with the provided email already exists.
    """
    try:
        new_user = auth_service.register_new_user(user_data)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and get JWT token",
    description="Authenticates a user with email and password, returning an access token upon success."
)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticates a user and returns a JWT access token.

    - **email**: The user's email address.
    - **password**: The user's password.

    **Returns**:
    - `200 OK`: An access token and token type if authentication is successful.

    **Raises**:
    - `401 Unauthorized`: If the provided email or password is incorrect.
    """
    user = auth_service.authenticate_user_login(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.generate_jwt_token(user.id)
    return Token(access_token=access_token)