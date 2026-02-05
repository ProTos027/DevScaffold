from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# Assuming 'Base' is defined in a separate database configuration file, e.g., app/database/base.py
# For simplicity, if not provided elsewhere, it would typically look like:
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()

# --- SQLAlchemy ORM Model ---
# This is the SQLAlchemy model that maps to the 'pieces' table in the database.

# NOTE: Replace 'Base' with your actual SQLAlchemy declarative base import
# Example: from app.database.base import Base

# Placeholder for Base if not imported from elsewhere. In a real FastAPI app,
# you'd import it from your db setup (e.g., from app.database import Base)
class Base:
    __abstract__ = True
    pass

class Piece(Base):
    __tablename__ = "pieces"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True) # e.g., 'pawn', 'rook', 'king'
    color = Column(String, index=True) # e.g., 'white', 'black'
    position_x = Column(Integer)
    position_y = Column(Integer)
    game_id = Column(Integer, ForeignKey("games.id")) # Assumes a 'games' table with 'id'

    # Optional: Define relationship if a 'Game' model exists
    # game = relationship("Game", back_populates="pieces")


# --- Pydantic Schemas ---
# These schemas define the data structure for API requests and responses.

class PieceBase(BaseModel):
    type: str = Field(..., description="Type of the chess piece (e.g., 'pawn', 'rook')")
    color: str = Field(..., description="Color of the piece ('white' or 'black')")
    position_x: int = Field(..., ge=0, le=7, description="X-coordinate (column) on the board")
    position_y: int = Field(..., ge=0, le=7, description="Y-coordinate (row) on the board")
    game_id: int = Field(..., description="ID of the game this piece belongs to")

class PieceCreate(PieceBase):
    # No additional fields needed for creation beyond PieceBase for now
    pass

class PieceUpdate(PieceBase):
    # Fields can be optional for update operations
    type: Optional[str] = None
    color: Optional[str] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    game_id: Optional[int] = None # Generally, game_id shouldn't change, but made optional for flexibility

class PieceInDBBase(PieceBase):
    id: int = Field(..., description="Unique identifier for the piece")

    model_config = ConfigDict(from_attributes=True) # Enables ORM mode for Pydantic v2

# Schema for reading a piece (e.g., when returning a piece from the API)
class Piece(PieceInDBBase):
    pass

# Schema for a list of pieces, if needed
class PieceList(BaseModel):
    pieces: list[Piece]
