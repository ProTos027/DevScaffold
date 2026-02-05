from typing import Optional
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., example="Buy groceries")
    description: Optional[str] = Field(None, example="Milk, eggs, bread, butter")
    completed: bool = Field(False, example=False)


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Buy more groceries")
    description: Optional[str] = Field(None, example="Add cheese and fruits")
    completed: Optional[bool] = Field(None, example=True)


class Todo(TodoBase):
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True
