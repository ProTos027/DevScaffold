from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetimenn# Base Pydantic models for request/responsenclass UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Allow ORM model to Pydantic model conversion

