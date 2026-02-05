from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Basennclass BoardState(Base):
    __tablename__ = "board_states"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    fen_string = Column(String, nullable=False) # Forsyth-Edwards Notation for board staten    move_number = Column(Integer, nullable=False) # The move number this state represents
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    game = relationship("Game", back_populates="board_states")

    def __repr__(self):
        return f"<BoardState(id={self.id}, game_id={self.game_id}, move_number={self.move_number})>"