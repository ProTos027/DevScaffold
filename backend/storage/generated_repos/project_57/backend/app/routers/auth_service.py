from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuration (ideally from environment variables or a config file)
SECRET_KEY = "super-secret-key-replace-me-with-a-real-one"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock database
# In a real application, this would interact with a database (SQLAlchemy, MongoDB, etc.)
fake_users_db = {}

# --- Models ---

# Base User model (used for response or when fetching from DB without password)
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Model for creating a new user (includes password)
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

# Model for user stored in the database (includes hashed password)
class UserInDB(User):
    hashed_password: str

# Model for JWT token data
class TokenData(BaseModel):
    username: Optional[str] = None

# --- Utility functions ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- Core Service Functions ---

def register_user(user_data: UserCreate) -> Optional[User]:
    """
    Registers a new user by hashing their password and storing them in the mock database.
    Returns the created user (without password) or None if the username already exists.
    """
    if user_data.username in fake_users_db:
        return None  # User already exists

    hashed_password = get_password_hash(user_data.password)
    user_in_db = UserInDB(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )
    fake_users_db[user_data.username] = user_in_db
    return User(**user_in_db.dict(exclude={'hashed_password'}))

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticates a user by checking their username and password.
    Returns the user (without password) if authenticated, otherwise None.
    """
    user_in_db = fake_users_db.get(username)
    if not user_in_db:
        return None
    if not verify_password(password, user_in_db.hashed_password):
        return None
    return User(**user_in_db.dict(exclude={'hashed_password'}))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """
    Verifies a JWT token and extracts its data.
    Returns TokenData if valid, otherwise None (after handling JWTError).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    return token_data
