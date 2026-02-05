from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., example="johndoe")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="securepassword")

class User(UserBase):
    id: int = Field(..., example=1)
    is_active: bool = Field(True, example=True)

    class ConfigDict:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None