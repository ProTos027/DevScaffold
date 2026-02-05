from typing import List, Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from app.games.models import GameStatus, PieceColor


class PieceBase(BaseModel):
    piece_type: str
    color: PieceColor
    position_x: int = Field(ge=0, le=7)
    position_y: int = Field(ge=0, le=7)


class PieceResponse(PieceBase):
    id: int
    is_captured: bool
    moved: bool

    model_config = {"from_attributes": True}


class BoardBase(BaseModel):
    state: List[List[Optional[Dict[str, Any]]]] # Example: [['R', 'N', ...], [...]] or more detailed dicts
    last_move_san: Optional[str] = None
    fen: Optional[str] = None
    castling_rights: str
    en_passant_target: Optional[str] = None
    halfmove_clock: int
    fullmove_number: int


class BoardResponse(BoardBase):
    id: int
    pieces: List[PieceResponse]

    model_config = {"from_attributes": True}


class GameCreate(BaseModel):
    title: Optional[str] = "New Game"
    variant_name: Optional[str] = "Standard Chess"


class GameResponse(BaseModel):
    id: int
    title: str
    variant_name: str
    created_at: datetime
    status: GameStatus
    current_turn: PieceColor
    current_player_id: Optional[int] = None
    player_white_id: Optional[int] = None
    player_black_id: Optional[int] = None
    board: Optional[BoardResponse] = None

    model_config = {"from_attributes": True}


class MoveRequest(BaseModel):
    from_x: int = Field(ge=0, le=7)
    from_y: int = Field(ge=0, le=7)
    to_x: int = Field(ge=0, le=7)
    to_y: int = Field(ge=0, le=7)
    promotion_choice: Optional[str] = None # e.g., 'Queen', 'Knight', 'Rook', 'Bishop'
