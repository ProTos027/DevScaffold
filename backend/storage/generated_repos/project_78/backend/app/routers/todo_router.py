from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import TodoCreate, TodoUpdate, TodoResponse
from app.services import todo_service
from app.dependencies import auth_middleware
from app.models.user import User as DBUser

router = APIRouter()

@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_item(
    todo_create: TodoCreate,
    current_user: DBUser = Depends(auth_middleware.get_current_user)
):
    """Create a new Todo item for the authenticated user."""
    new_todo = await todo_service.create_todo(user_id=current_user.id, todo_data=todo_create)
    return new_todo

@router.get("/todos", response_model=List[TodoResponse])
async def get_all_todos(
    current_user: DBUser = Depends(auth_middleware.get_current_user)
):
    """Retrieve all Todo items for the authenticated user."""
    todos = await todo_service.get_all_todos(user_id=current_user.id)
    return todos

@router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo_by_id(
    todo_id: int,
    current_user: DBUser = Depends(auth_middleware.get_current_user)
):
    """Retrieve a specific Todo item by its ID, belonging to the authenticated user."""
    todo = await todo_service.get_todo_by_id(todo_id=todo_id, user_id=current_user.id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@router.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo_item(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: DBUser = Depends(auth_middleware.get_current_user)
):
    """Update an existing Todo item belonging to the authenticated user."""
    updated_todo = await todo_service.update_todo(todo_id=todo_id, user_id=current_user.id, todo_data=todo_update)
    if not updated_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not authorized")
    return updated_todo

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_item(
    todo_id: int,
    current_user: DBUser = Depends(auth_middleware.get_current_user)
):
    """Delete a Todo item belonging to the authenticated user."""
    deleted = await todo_service.delete_todo(todo_id=todo_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not authorized")
    # No content returned for 204 status
    return