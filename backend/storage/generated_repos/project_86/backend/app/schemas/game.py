from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetimenn# Piece Schemasnclass PieceBaseSch(BaseModel):
    piece_type: str = Field(..., description="Type of the piece, e.g., 'King', 'Rook', 'CustomPawn'")
    color: str = Field(..., description="Color of the piece, 'white' or 'black'")
    position_x: int = Field(..., ge=0, le=7, description="X-coordinate (column) of the piece, 0-7")
    position_y: int = Field(..., ge=0, le=7, description="Y-coordinate (row) of the piece, 0-7")

class PieceCreateSch(PieceBaseSch):
    game_id: int

class PieceUpdateSch(BaseModel):
    piece_type: Optional[str] = None
    color: Optional[str] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    is_captured: Optional[bool] = None

class PieceResponseSch(PieceBaseSch):
    id: int
    game_id: int
    is_captured: bool

    class Config:
        from_attributes = True

# BoardState Schemas
class BoardStateBaseSch(BaseModel):
    fen_string: str = Field(..., description="Forsyth-Edwards Notation (FEN) string representing the board state")
    move_number: int = Field(..., ge=0, description="The move number this state represents")

class BoardStateCreateSch(BoardStateBaseSch):
    game_id: int

class BoardStateUpdateSch(BaseModel):
    fen_string: Optional[str] = None
    move_number: Optional[int] = None

class BoardStateResponseSch(BoardStateBaseSch):
    id: int
    game_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Game Schemas
class GameBase(BaseModel):
    pass

class GameCreate(GameBase):
    # For simplicity, games start with player1 only and wait for player2
    # Custom rules might be defined here later
    initial_fen: str = Field("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", description="Initial FEN string for the game")

class GameUpdateState(BaseModel):
    player2_id: Optional[int] = None
    status: Optional[str] = None # 'in_progress', 'finished', 'aborted', 'waiting_for_player'
    current_turn: Optional[int] = None # 1 for player1, 2 for player2
    winner_id: Optional[int] = None
    end_time: Optional[datetime] = None

class GameResponse(GameBase):
    id: int
    player1_id: int
    player2_id: Optional[int] = None
    status: str
    current_turn: int
    winner_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    # Potentially include player usernames later

    class Config:
        from_attributes = True

class GameFullStateResponse(GameResponse):
    board_states: List[BoardStateResponseSch]
    pieces: List[PieceResponseSch]

    class Config:
        from_attributes = True