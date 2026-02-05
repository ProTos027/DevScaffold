from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate

class TodoService:
    def create_user_todo(self, db: Session, todo_create_schema: TodoCreate, user_id: int) -> Todo:
        db_todo = Todo(**todo_create_schema.model_dump(), owner_id=user_id)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def get_todos(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Todo]:
        return db.query(Todo).filter(Todo.owner_id == user_id).offset(skip).limit(limit).all()

    def get_todo(self, db: Session, todo_id: int, user_id: int) -> Todo:
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
        if db_todo.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this Todo")
        return db_todo

    def update_todo(self, db: Session, todo_id: int, todo_update_schema: TodoUpdate, user_id: int) -> Todo:
        db_todo = self.get_todo(db, todo_id, user_id) # Enforce ownership and check existence

        update_data = todo_update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)

        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def delete_todo(self, db: Session, todo_id: int, user_id: int):
        db_todo = self.get_todo(db, todo_id, user_id) # Enforce ownership and check existence

        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted successfully"}
