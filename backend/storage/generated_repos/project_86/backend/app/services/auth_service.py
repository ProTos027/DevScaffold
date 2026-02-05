from datetime import datetime, timedelta
from typing import Optional

import jwt
import bcrypt
from fastapi import HTTPException, status
from pydantic import BaseModel

# --- Placeholder for User Model (assuming it's defined elsewhere, e.g., app.models.user) ---
# In a real application, you would import User from app.models.user
# For the purpose of this single file generation, we'll define a basic User model here.
class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    hashed_password: str

    # Simulate a database for demonstration purposes
    _next_id = 1
    _users_db = {}

    @classmethod
    def create(cls, username: str, email: str, hashed_password: str):
        if cls.find_by_username(username) or cls.find_by_email(email):
            return None # User already exists
        new_user = cls(id=cls._next_id, username=username, email=email, hashed_password=hashed_password)
        cls._users_db[username] = new_user
        cls._next_id += 1
        return new_user

    @classmethod
    def find_by_username(cls, username: str):
        return cls._users_db.get(username)

    @classmethod
    def find_by_email(cls, email: str):
        for user in cls._users_db.values():
            if user.email == email:
                return user
        return None

    @classmethod
    def find_by_id(cls, user_id: int):
        for user in cls._users_db.values():
            if user.id == user_id:
                return user
        return None

# --- Placeholder for Configuration (assuming it's defined elsewhere, e.g., app.config) ---
# In a real application, you would import settings from app.config
# For the purpose of this single file generation, we'll define basic settings here.
class Settings:
    SECRET_KEY: str = "your-super-secret-key-please-change-it"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

class AuthService:
    def __init__(self):
        pass # No explicit dependencies needed here with our simulated DB

    def hash_password(self, password: str) -> str:
        """Hashes a plain text password using bcrypt."""
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain text password against a hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username: str, email: str, password: str) -> User:
        """Registers a new user after hashing their password."""
        if User.find_by_username(username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
        if User.find_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed_password = self.hash_password(password)
        user = User.create(username=username, email=email, hashed_password=hashed_password)
        if not user:
            # This case should ideally be caught by the prior checks, but good for robustness
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register user")
        return user

    def login_user(self, username: str, password: str) -> User:
        """Authenticates a user by verifying their credentials."""
        user = User.find_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

    def create_jwt_token(self, user_id: int) -> str:
        """Generates a JWT token for the given user ID."""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_jwt_token(self, token: str) -> Optional[int]:
        """Validates a JWT token and returns the user ID if valid, otherwise None or raises an error."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: int = int(payload.get("sub"))
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials: User ID missing")
            
            # Optionally, you might want to check if the user still exists in the DB
            # if not User.find_by_id(user_id):
            #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
                
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials: {e}")

