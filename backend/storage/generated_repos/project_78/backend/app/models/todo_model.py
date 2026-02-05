from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.database.base import Base # Assuming Base is defined here

# SQLAlchemy ORM model
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id")) # Assuming a 'users' table exists

    owner = relationship("User", back_populates="todos") # Assuming a 'User' ORM model with 'todos' back_populates

# Pydantic Schemas

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoInDBBase(TodoBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True) # Enable ORM mode for Pydantic v2


class Todo(TodoInDBBase):
    # Additional fields can be added here if needed for the response
    pass
