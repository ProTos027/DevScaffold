from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Basennclass Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String, default="waiting_for_player") # e.g., 'waiting_for_player', 'in_progress', 'finished', 'aborted'
    current_turn = Column(Integer, default=1) # 1 for player1, 2 for player2
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)

    # Relationships
    player1 = relationship("User", back_populates="games_as_player1", foreign_keys="[Game.player1_id]")
    player2 = relationship("User", back_populates="games_as_player2", foreign_keys="[Game.player2_id]")
    winner = relationship("User", back_populates="games_won", foreign_keys="[Game.winner_id]")
    board_states = relationship("BoardState", back_populates="game", cascade="all, delete-orphan")
    pieces = relationship("Piece", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game(id={self.id}, player1_id={self.player1_id}, player2_id={self.player2_id}, status='{self.status}')>"