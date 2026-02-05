from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    email: EmailStr = Field(..., example="john.doe@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="StrongP@ssw0rd")


class User(UserBase):
    id: UUID = Field(default_factory=uuid4, example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2023-10-27T10:00:00.123456Z")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2023-10-27T10:00:00.123456Z")
    password_hash: str = Field(..., example="$2b$12$EXAMPLEHASHFORPASSWORDabc123def456ghi789jkl012mno345pqr678stu901vwx234yz567")

    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    pass
