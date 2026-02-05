from pydantic import BaseModel, Field
from typing import Optional

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="Buy groceries")
    description: Optional[str] = Field(None, max_length=500, example="Milk, eggs, bread")
    completed: bool = Field(False, example=False)

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    title: Optional[str] = Field(None, min_length=1, max_length=100, example="Buy milk")
    description: Optional[str] = Field(None, max_length=500, example="Fresh organic milk")
    completed: Optional[bool] = Field(None, example=True)

class Todo(TodoBase):
    id: int = Field(..., example=1)
    owner_id: int = Field(..., example=1)

    class ConfigDict:
        from_attributes = True