from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# SQLAlchemy ORM model
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

# Pydantic schemas

class UserBase(BaseModel):
    username: str = Field(..., example="john_doe")

class UserCreate(UserBase):
    password: str = Field(..., example="SecureP@ssw0rd")

class User(UserBase):
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2023-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2023-01-01T12:00:00Z")

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str = Field(..., example="$2b$12$EXAMPLEHASHSTRING")