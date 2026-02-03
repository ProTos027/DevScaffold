from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, Field
from datetime import datetime

# SQLAlchemy ORM Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)

# Pydantic Schemas
class UserBase(BaseModel):
    # No user-provided fields for creation or update are specified.
    # All required fields (id, created_at, updated_at) are database-managed.
    pass

class UserCreate(UserBase):
    # For creating a user. As no specific user-input fields are defined,
    # this model remains empty, implying the database handles initial values.
    pass

class UserUpdate(UserBase):
    # For updating a user. As no specific user-updatable fields are defined,
    # this model remains empty, implying updates are handled internally or not exposed.
    pass

class UserResponse(UserBase):
    id: int = Field(..., description="Unique identifier for the user.")
    created_at: datetime = Field(..., description="Timestamp when the user record was created.")
    updated_at: datetime = Field(..., description="Timestamp when the user record was last updated.")

    class Config:
        orm_mode = True  # Deprecated in Pydantic v2, but kept for compatibility
        from_attributes = True # For Pydantic v2