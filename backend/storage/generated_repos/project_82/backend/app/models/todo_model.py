from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base  # Assuming Base is defined in app/database.py


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))  # Assuming a 'users' table and User model exists
    abc = Column(String, nullable=True)

    # Define the relationship to the User model
    # Note: 'User' should be imported or defined elsewhere if this model is in a separate file.
    # For simplicity, we assume 'User' class will be known at runtime (e.g., imported or defined in the same module)
    owner = relationship("User", back_populates="todos")

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}', completed={self.completed})>"