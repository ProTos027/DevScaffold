from typing import List, Annotated
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status

# Assuming todo_service.py is in the same directory for relative import
# In a larger project, this might be from `app.services.todo_service`
from app.routers.todo_service import TodoService, User, TodoCreate, TodoUpdate, Todo, todo_service

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)

# --- Dependency for current user (placeholder) ---
# In a real application, this would come from an authentication module
# e.g., from app.dependencies.auth import get_current_active_user
async def get_current_user() -> User:
    # Simulate an authenticated user. In a real app, this would validate a token.
    # For demonstration, we'll use a fixed user ID.
    # Replace with actual authentication logic (e.g., JWT token decoding).
    mock_user_id = UUID("a1b2c3d4-e5f6-7890-1234-567890abcdef")
    return User(id=mock_user_id, username="testuser")

# Type alias for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]

# --- API Endpoints ---

@router.post("/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_new_todo(todo_data: TodoCreate, current_user: CurrentUser):
    """Create a new Todo item for the current user."""
    return todo_service.create_todo(todo_data, current_user)

@router.get("/", response_model=List[Todo])
async def get_all_todos(current_user: CurrentUser):
    """Retrieve all Todo items belonging to the current user."""
    return todo_service.get_todos(current_user)

@router.get("/{todo_id}", response_model=Todo)
async def get_single_todo(todo_id: UUID, current_user: CurrentUser):
    """Retrieve a specific Todo item by its ID for the current user."""
    return todo_service.get_todo_by_id(todo_id, current_user)

@router.put("/{todo_id}", response_model=Todo)
async def update_existing_todo(todo_id: UUID, todo_update_data: TodoUpdate, current_user: CurrentUser):
    """Update an existing Todo item (title, description, completion status) by ID."""
    return todo_service.update_todo(todo_id, todo_update_data, current_user)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_todo(todo_id: UUID, current_user: CurrentUser):
    """Delete a Todo item by its ID."""
    todo_service.delete_todo(todo_id, current_user)
    return
