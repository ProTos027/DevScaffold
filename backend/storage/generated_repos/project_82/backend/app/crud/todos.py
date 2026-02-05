from sqlalchemy.orm import Session
from app.db import models
from app.schemas import todos as schemas

def get_todo(db: Session, todo_id: int, user_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()

def get_todos(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_todo(db: Session, todo: schemas.TodoCreate, user_id: int):
    db_todo = models.Todo(**todo.model_dump(), owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, db_todo: models.Todo, todo_update: schemas.TodoUpdate):
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, db_todo: models.Todo):
    db.delete(db_todo)
    db.commit()
    return db_todo