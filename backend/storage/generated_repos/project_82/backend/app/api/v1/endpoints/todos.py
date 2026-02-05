from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import todos as todo_schemas
from app.crud import todos as crud_todos
from app.crud import users as crud_users
from app.core import security

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.post("/", response_model=todo_schemas.Todo, status_code=status.HTTP_201_CREATED)
def create_todo_for_user(
    todo: todo_schemas.TodoCreate,
    current_user_email: Annotated[str, Depends(security.get_current_user_email)],
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=current_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return crud_todos.create_user_todo(db=db, todo=todo, user_id=user.id)

@router.get("/", response_model=List[todo_schemas.Todo])
def read_todos(
    current_user_email: Annotated[str, Depends(security.get_current_user_email)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=current_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    todos = crud_todos.get_todos(db, user_id=user.id, skip=skip, limit=limit)
    return todos

@router.get("/{todo_id}", response_model=todo_schemas.Todo)
def read_todo(
    todo_id: int,
    current_user_email: Annotated[str, Depends(security.get_current_user_email)],
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=current_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_todo = crud_todos.get_todo(db, todo_id=todo_id, user_id=user.id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not owned by user")
    return db_todo

@router.put("/{todo_id}", response_model=todo_schemas.Todo)
def update_todo(
    todo_id: int,
    todo: todo_schemas.TodoUpdate,
    current_user_email: Annotated[str, Depends(security.get_current_user_email)],
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=current_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_todo = crud_todos.get_todo(db, todo_id=todo_id, user_id=user.id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not owned by user")
    return crud_todos.update_todo(db=db, db_todo=db_todo, todo_update=todo)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    current_user_email: Annotated[str, Depends(security.get_current_user_email)],
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=current_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_todo = crud_todos.get_todo(db, todo_id=todo_id, user_id=user.id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not owned by user")
    crud_todos.delete_todo(db=db, db_todo=db_todo)
    return {"message": "Todo deleted successfully"}