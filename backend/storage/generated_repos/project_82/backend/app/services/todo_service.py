from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.todo import Todo as DBTodoModel
from app.schemas.todo import TodoCreate, TodoUpdate

def create_todo(
    db: Session, todo_create: TodoCreate, user_id: int
) -> DBTodoModel:
    db_todo = DBTodoModel(
        title=todo_create.title,
        description=todo_create.description,
        owner_id=user_id,
        completed=todo_create.completed  # Assign default or provided value
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todo(db: Session, todo_id: int, user_id: int) -> Optional[DBTodoModel]:
    return (
        db.query(DBTodoModel)
        .filter(DBTodoModel.id == todo_id, DBTodoModel.owner_id == user_id)
        .first()
    )

def get_all_todos(db: Session, user_id: int) -> List[DBTodoModel]:
    return db.query(DBTodoModel).filter(DBTodoModel.owner_id == user_id).all()

def update_todo(
    db: Session, todo_id: int, todo_update: TodoUpdate, user_id: int
) -> Optional[DBTodoModel]:
    db_todo = (
        db.query(DBTodoModel)
        .filter(DBTodoModel.id == todo_id, DBTodoModel.owner_id == user_id)
        .first()
    )
    if db_todo:
        update_data = todo_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int, user_id: int) -> Optional[DBTodoModel]:
    db_todo = (
        db.query(DBTodoModel)
        .filter(DBTodoModel.id == todo_id, DBTodoModel.owner_id == user_id)
        .first()
    )
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo
