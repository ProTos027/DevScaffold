from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from fastapi import HTTPException, status

# --- Pydantic Models (normally in app/models) ---

# Placeholder User model for dependency injection
class User(BaseModel):
    id: UUID
    username: str

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=1024)
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=1024)
    completed: Optional[bool] = None

class Todo(TodoBase):
    id: UUID
    owner_id: UUID

    class Config:
        from_attributes = True

# --- In-memory database (for demonstration) ---
# In a real application, this would be an ORM like SQLAlchemy
# interacting with a proper database (PostgreSQL, MySQL, etc.)
_todos_db: List[Todo] = []

class TodoService:

    def create_todo(self, todo_data: TodoCreate, current_user: User) -> Todo:
        """Create a new Todo item associated with the current user."""
        new_todo = Todo(
            id=uuid4(),
            owner_id=current_user.id,
            title=todo_data.title,
            description=todo_data.description,
            completed=todo_data.completed
        )
        _todos_db.append(new_todo)
        return new_todo

    def get_todos(self, current_user: User) -> List[Todo]:
        """Retrieve all Todo items for the authenticated user."""
        return [todo for todo in _todos_db if todo.owner_id == current_user.id]

    def get_todo_by_id(self, todo_id: UUID, current_user: User) -> Todo:
        """Retrieve a specific Todo item by ID for the authenticated user."""
        for todo in _todos_db:
            if todo.id == todo_id:
                if todo.owner_id != current_user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this todo item")
                return todo
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")

    def update_todo(self, todo_id: UUID, todo_update_data: TodoUpdate, current_user: User) -> Todo:
        """Update an existing Todo item (title, description, completion status)."""
        for index, todo in enumerate(_todos_db):
            if todo.id == todo_id:
                if todo.owner_id != current_user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this todo item")

                update_data = todo_update_data.model_dump(exclude_unset=True)
                updated_todo = todo.model_copy(update=update_data)
                _todos_db[index] = updated_todo
                return updated_todo
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")

    def delete_todo(self, todo_id: UUID, current_user: User):
        """Facilitate deletion of Todo items."""
        for index, todo in enumerate(_todos_db):
            if todo.id == todo_id:
                if todo.owner_id != current_user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this todo item")
                _todos_db.pop(index)
                return {"message": "Todo item deleted successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")

# Instantiate the service (singleton pattern for simplicity)
todo_service = TodoService()
