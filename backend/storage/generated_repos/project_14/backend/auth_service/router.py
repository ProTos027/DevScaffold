import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# --- Configuration (Replace with environment variables in a real app) ---
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Data Models ---

class UserBase(BaseModel):
    username: str = Field(..., example="john_doe")
    email: Optional[str] = Field(None, example="john.doe@example.com")

class UserCreate(UserBase):
    password: str = Field(..., example="SecureP@ssw0rd123")

class UserInDB(UserBase):
    id: int
    hashed_password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True # For compatibility with ORM models if used

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Mock Database (Replace with a real database in a production app) ---
fake_users_db = {}
user_id_counter = 0

def get_user_from_db(username: str) -> Optional[UserInDB]:
    """Simulates fetching a user from the database by username."""
    for user_id, user_data in fake_users_db.items():
        if user_data["username"] == username:
            return UserInDB(**user_data)
    return None

# --- Security Functions ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticates a user by username and password."""
    user = get_user_from_db(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Dependency to get the current authenticated user from the access token.
    Raises HTTPException if the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- APIRouter Definition ---
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# --- Router Endpoints ---

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user with a unique username and email, hashing their password.",
)
async def register_new_user(user_data: UserCreate):
    """
    Registers a new user in the system.

    - **username**: Must be unique.
    - **email**: Optional, but if provided, should be unique.
    - **password**: The user's chosen password.
    """
    if get_user_from_db(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    # In a real app, you might also check for email uniqueness if required
    # if user_data.email and any(u["email"] == user_data.email for u in fake_users_db.values()):
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Email already registered"
    #     )

    hashed_password = get_password_hash(user_data.password)
    global user_id_counter
    user_id_counter += 1
    new_user_in_db = UserInDB(
        id=user_id_counter,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    fake_users_db[new_user_in_db.id] = new_user_in_db.dict()
    return UserResponse(**new_user_in_db.dict())

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and get access token",
    description="Authenticates a user with username and password, returning an access token upon success.",
)
async def authenticate_user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user using username and password.

    - **username**: The user's username.
    - **password**: The user's password.

    Returns an access token if authentication is successful.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Fetch current user profile",
    description="Retrieves the profile of the currently authenticated user.",
)
async def fetch_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Fetches the profile information of the user whose access token is provided.

    Requires a valid JWT access token in the Authorization header (Bearer token).
    """
    return UserResponse(**current_user.dict())