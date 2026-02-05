from pydantic import BaseModel

class TodoBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    title: str | None = None
    completed: bool | None = None

class Todo(TodoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True # Pydantic V2