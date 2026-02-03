from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="StrongPassword123!")


class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(None, example="new_user@example.com")
    password: Optional[str] = Field(None, min_length=8, example="NewStrongPassword456!")


class UserInDBBase(UserBase):
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2023-10-27T10:00:00.000000+00:00")

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDBBase):
    # This schema is for API responses, so password_hash should not be included
    pass


class UserInDB(UserInDBBase):
    # This schema includes the password_hash for internal use (e.g., authentication)
    password_hash: str = Field(..., example="$2b$12$examplehashstring...")