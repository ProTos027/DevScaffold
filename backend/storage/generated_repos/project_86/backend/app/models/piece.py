from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Basennclass Piece(Base):
    __tablename__ = "pieces"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    piece_type = Column(String, nullable=False) # e.g., 'King', 'Queen', 'CustomPawn'
    color = Column(String, nullable=False) # 'white' or 'black'
    position_x = Column(Integer, nullable=False) # 0-7
    position_y = Column(Integer, nullable=False) # 0-7
    is_captured = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    game = relationship("Game", back_populates="pieces")

    def __repr__(self):
        return f"<Piece(id={self.id}, game_id={self.game_id}, type='{self.piece_type}', color='{self.color}', pos=({self.position_x},{self.position_y}))>"