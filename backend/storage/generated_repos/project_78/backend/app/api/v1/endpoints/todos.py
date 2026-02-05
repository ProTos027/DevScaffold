from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.todo import Todo, TodoCreate, TodoUpdate
from app.schemas.user import User as UserSchema
from app.models.user import User as DBUser
from app.crud import todo as crud_todo
from app.core import dependencies

router = APIRouter()

@router.post("/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo_for_current_user(
    todo: TodoCreate,
    current_user: Annotated[DBUser, Depends(dependencies.get_current_active_user)],
    db: Session = Depends(get_db)
):
    return crud_todo.create_user_todo(db=db, todo=todo, owner_id=current_user.id)

@router.get("/", response_model=List[Todo])
def read_todos_for_current_user(
    current_user: Annotated[DBUser, Depends(dependencies.get_current_active_user)],
    db: Session = Depends(get_db)
):
    todos = crud_todo.get_todos_by_owner(db=db, owner_id=current_user.id)
    return todos

@router.get("/{todo_id}", response_model=Todo)
def read_todo(
    todo_id: int,
    current_user: Annotated[DBUser, Depends(dependencies.get_current_active_user)],
    db: Session = Depends(get_db)
):
    todo = crud_todo.get_todo(db, todo_id=todo_id)
    if not todo or todo.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: Annotated[DBUser, Depends(dependencies.get_current_active_user)],
    db: Session = Depends(get_db)
):
    todo = crud_todo.get_todo(db, todo_id=todo_id)
    if not todo or todo.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not owned by user")
    
    updated_todo = crud_todo.update_todo(db, todo_id=todo_id, todo_update=todo_update)
    if not updated_todo:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update todo")
    return updated_todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    current_user: Annotated[DBUser, Depends(dependencies.get_current_active_user)],
    db: Session = Depends(get_db)
):
    todo = crud_todo.get_todo(db, todo_id=todo_id)
    if not todo or todo.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not owned by user")
    
    if not crud_todo.delete_todo(db, todo_id=todo_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete todo")
    return {"message": "Todo deleted successfully"}