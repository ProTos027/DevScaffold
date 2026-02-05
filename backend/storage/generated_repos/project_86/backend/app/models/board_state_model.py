from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field

Base = declarative_base()

class BoardState(Base):
    __tablename__ = "board_states"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True, nullable=False) # Assuming game_id is a string, e.g., UUID
    fen_string = Column(String, nullable=False)
    move_number = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<BoardState(id={self.id}, game_id='{self.game_id}', move_number={self.move_number})>"

class BoardStateBase(BaseModel):
    game_id: str = Field(..., description="The unique identifier for the game.")
    fen_string: str = Field(..., description="FEN string representation of the board state.")
    move_number: int = Field(..., description="The sequential move number in the game.")

class BoardStateCreate(BoardStateBase):
    pass

class BoardStateRead(BoardStateBase):
    id: int = Field(..., description="The unique identifier for the board state.")

    class Config:
        orm_mode = True # Enable ORM mode for Pydantic