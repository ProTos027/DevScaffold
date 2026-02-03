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
    SQLAlchemy ORM model for storing user data.

    Responsibilities:
    - store_user_data: Represents the structure for saving user records to the database.
    - fetch_user_data: Defines the structure for retrieving user records from the database.
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, unique=True, index=True, nullable=False)
    password_hash: str = Column(String, nullable=False)
    created_at: datetime.datetime = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

# --- Pydantic Schema for API Responses ---

class UserResponse(BaseModel):
    """
    Pydantic schema for representing user data in API responses.
    Excludes sensitive information like password_hash.
    """
    id: int = Field(..., description="Unique identifier for the user.")
    email: EmailStr = Field(..., description="User's email address, must be unique.")
    created_at: datetime.datetime = Field(..., description="Timestamp when the user account was created.")

    class Config:
        from_attributes = True # Enable ORM mode for Pydantic v2+