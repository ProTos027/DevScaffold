from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Basennclass User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    games_as_player1 = relationship("Game", back_populates="player1", foreign_keys="[Game.player1_id]")
    games_as_player2 = relationship("Game", back_populates="player2", foreign_keys="[Game.player2_id]")
    games_won = relationship("Game", back_populates="winner", foreign_keys="[Game.winner_id]")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"