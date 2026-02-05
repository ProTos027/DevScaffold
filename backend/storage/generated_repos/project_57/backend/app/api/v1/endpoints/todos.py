from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.todo import Todo, TodoCreate, TodoUpdate
from app.schemas.user import User
from app.crud.todo import get_todo, get_todos, create_user_todo, update_todo, delete_todo
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.core.exceptions import TodoNotFoundException, UnauthorizedException

router = APIRouter()

@router.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED, summary="Create Todo", description="Create a new todo item for the current user.")
async def create_todo_for_current_user(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_user_todo(db=db, todo=todo, owner_id=current_user.id)

@router.get("/todos/", response_model=List[Todo], summary="Get All Todos", description="Retrieve all todo items for the current user.")
async def read_todos_for_current_user(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todos = get_todos(db, owner_id=current_user.id, skip=skip, limit=limit)
    return todos

@router.get("/todos/{todo_id}", response_model=Todo, summary="Get Todo by ID", description="Retrieve a specific todo item by its ID for the current user.")
async def read_todo_for_current_user(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_todo = get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise TodoNotFoundException()
    if db_todo.owner_id != current_user.id:
        raise UnauthorizedException(detail="Not authorized to access this todo item")
    return db_todo

@router.put("/todos/{todo_id}", response_model=Todo, summary="Update Todo", description="Update an existing todo item by its ID for the current user.")
async def update_todo_for_current_user(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_todo = get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise TodoNotFoundException()
    if db_todo.owner_id != current_user.id:
        raise UnauthorizedException(detail="Not authorized to update this todo item")
    return update_todo(db=db, db_todo=db_todo, todo_update=todo)

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Todo", description="Delete a todo item by its ID for the current user.")
async def delete_todo_for_current_user(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_todo = get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise TodoNotFoundException()
    if db_todo.owner_id != current_user.id:
        raise UnauthorizedException(detail="Not authorized to delete this todo item")
    delete_todo(db=db, todo_id=todo_id)
    return