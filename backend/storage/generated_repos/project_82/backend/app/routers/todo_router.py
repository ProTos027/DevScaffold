from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate
from app.schemas.user import User
from app.services.todo_service import TodoService

# Initialize the APIRouter with a prefix and tags
router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Todo item for the authenticated user."""
    todo_service = TodoService(db)
    return todo_service.create_todo(todo=todo, user_id=current_user.id)

@router.get("/", response_model=List[TodoOut])
async def read_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all Todo items belonging to the authenticated user."""
    todo_service = TodoService(db)
    return todo_service.get_todos(user_id=current_user.id)

@router.get("/{todo_id}", response_model=TodoOut)
async def read_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a specific Todo item by its ID for the authenticated user."""
    todo_service = TodoService(db)
    todo = todo_service.get_todo(todo_id=todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoOut)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing Todo item by its ID for the authenticated user."""
    todo_service = TodoService(db)
    updated_todo = todo_service.update_todo(todo_id=todo_id, todo_update=todo_update, user_id=current_user.id)
    if updated_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not authorized")
    return updated_todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a Todo item by its ID for the authenticated user."""
    todo_service = TodoService(db)
    success = todo_service.delete_todo(todo_id=todo_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not authorized")
    return {"message": "Todo deleted successfully"}
