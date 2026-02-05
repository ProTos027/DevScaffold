from sqlalchemy.orm import Session

from app.models.todo import Todo as DBTodo
from app.schemas.todo import TodoCreate, TodoUpdate

def get_todo(db: Session, todo_id: int):
    return db.query(DBTodo).filter(DBTodo.id == todo_id).first()

def get_todos_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(DBTodo).filter(DBTodo.owner_id == owner_id).offset(skip).limit(limit).all()

def create_user_todo(db: Session, todo: TodoCreate, owner_id: int):
    db_todo = DBTodo(**todo.model_dump(), owner_id=owner_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate):
    db_todo = db.query(DBTodo).filter(DBTodo.id == todo_id).first()
    if not db_todo:
        return None
    
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int):
    db_todo = db.query(DBTodo).filter(DBTodo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False