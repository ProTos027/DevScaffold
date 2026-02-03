import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User  # Assuming app.models.user.User is your SQLAlchemy model

# --- Pydantic Models for Request/Response ---
# These models define the structure of data for API requests and responses.

class UserBase(BaseModel):
    """Base model for user data, including username and email."""
    username: str
    email: EmailStr

class UserRegisterRequest(UserBase):
    """Request model for user registration."""
    password: str

class UserLoginRequest(BaseModel):
    """Request model for user login."""
    username_or_email: str  # Can be username or email
    password: str

class UserResponse(UserBase):
    """Response model for user data, typically returned after registration or fetching user info."""
    id: int

    class Config:
        orm_mode = True  # Enable ORM mode for Pydantic to read directly from SQLAlchemy models

class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Model for data stored within a JWT token payload."""
    user_id: Optional[int] = None

# --- Configuration for JWT ---
# In a production application, SECRET_KEY should be loaded from environment variables
# and never hardcoded.
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-please-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer for extracting token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Helper Functions for Authentication ---

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        The bcrypt hashed password as a string.
    """
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a bcrypt hashed password.

    Args:
        plain_password: The plain text password provided by the user.
        hashed_password: The hashed password stored in the database.

    Returns:
        True if the passwords match, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_jwt_token(user_id: int) -> str:
    """
    Generates a JSON Web Token (JWT) for a given user ID.

    The token includes an expiration time.

    Args:
        user_id: The ID of the user for whom the token is generated.

    Returns:
        The encoded JWT as a string.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_jwt_token(token: str) -> TokenData:
    """
    Validates a JWT token and extracts the payload data.

    Raises:
        HTTPException: If the token is invalid, expired, or credentials cannot be validated.

    Args:
        token: The JWT token string.

    Returns:
        TokenData: An object containing the user ID from the token payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(user_id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Dependency for Current User ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency to retrieve the current authenticated user based on a JWT token.

    This function validates the token, extracts the user ID, and fetches the user
    object from the database.

    Args:
        token: The JWT token from the Authorization header (injected by OAuth2PasswordBearer).
        db: The database session dependency.

    Returns:
        User: The SQLAlchemy User object corresponding to the authenticated user.

    Raises:
        HTTPException: If the token is invalid, expired, or the user is not found.
    """
    token_data = validate_jwt_token(token)
    if token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# --- Endpoints ---

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.

    - **username**: A unique username for the new user.
    - **email**: A unique email address for the new user.
    - **password**: The plain text password for the new user.

    Raises:
        HTTPException: If the username or email is already registered.

    Returns:
        UserResponse: The newly created user's information (excluding password).
    """
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    # Hash the password using the helper function
    hashed_password = hash_password(user_data.password)

    # Create new user SQLAlchemy object
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the ID generated by the database

    return new_user

@router.post("/login", response_model=TokenResponse)
def login_user(user_credentials: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token upon successful login.

    - **username_or_email**: The user's username or email address.
    - **password**: The user's plain text password.

    Raises:
        HTTPException: If the provided credentials are incorrect.

    Returns:
        TokenResponse: An object containing the JWT access token and token type.
    """
    user = db.query(User).filter(
        (User.username == user_credentials.username_or_email) |
        (User.email == user_credentials.username_or_email)
    ).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token using the helper function
    access_token = generate_jwt_token(user.id)
    return TokenResponse(access_token=access_token)

# --- Example of a Protected Endpoint ---
# This endpoint demonstrates how to use the get_current_user dependency
# to protect routes that require authentication.

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current authenticated user's information.

    This endpoint requires a valid JWT token to be present in the
    `Authorization: Bearer <token>` header.

    Returns:
        UserResponse: The information of the currently authenticated user.
    """
    return current_user