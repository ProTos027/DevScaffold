from datetime import datetime

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from pydantic import BaseModel, EmailStr, Field

# --- SQLAlchemy ORM Model ---
Base = declarative_base()

class User(Base):
    """
    SQLAlchemy ORM model for storing user data.

    Fields:
    - id: Unique identifier for the user.
    - email: User's email address, must be unique.
    - password_hash: Hashed password for the user.
    - created_at: Timestamp when the user account was created.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

# --- Pydantic Schema for API Responses ---

class UserResponse(BaseModel):
    """
    Pydantic schema for API responses when fetching user data.
    Excludes sensitive information like password_hash for security.
    """
    id: int = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Timestamp when the user account was created")

    class Config:
        from_attributes = True # Enables ORM mode for Pydantic v2+