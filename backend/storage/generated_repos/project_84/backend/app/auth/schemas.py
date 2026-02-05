from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
