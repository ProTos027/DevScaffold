import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, Field

# --- SQLAlchemy ORM Model ---
Base = declarative_base()

class User(Base):
    """
    SQLAlchemy ORM model for a User.
    Manages user persistence in the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

# --- Pydantic Schemas ---

class UserSchema(BaseModel):
    """
    Pydantic schema for API responses representing a User.
    Excludes sensitive information like password_hash.
    """
    id: int
    email: EmailStr
    created_at: datetime.datetime

    class Config:
        orm_mode = True  # Enable ORM mode for direct conversion from SQLAlchemy models

class UserCreate(BaseModel):
    """
    Pydantic schema for creating a new User.
    Includes fields required for user registration.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64, description="Password for the user")

class UserUpdate(BaseModel):
    """
    Pydantic schema for updating an existing User.
    All fields are optional, allowing partial updates.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=64, description="New password for the user")