from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate

def get_todo(db: Session, todo_id: int) -> Todo | None:
    return db.query(Todo).filter(Todo.id == todo_id).first()

def get_todos(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Todo]:
    return db.query(Todo).filter(Todo.owner_id == owner_id).offset(skip).limit(limit).all()

def create_user_todo(db: Session, todo: TodoCreate, owner_id: int) -> Todo:
    db_todo = Todo(**todo.model_dump(), owner_id=owner_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, db_todo: Todo, todo_update: TodoUpdate) -> Todo:
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int) -> Todo | None:
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo