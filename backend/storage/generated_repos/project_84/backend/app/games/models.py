from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class GameStatus(str, enum.Enum):
    WAITING_FOR_PLAYERS = "waiting_for_players"
    IN_PROGRESS = "in_progress"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"
    ABANDONED = "abandoned"


class PieceColor(str, enum.Enum):
    WHITE = "white"
    BLACK = "black"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Game")
    variant_name = Column(String, default="Standard Chess")
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(GameStatus), default=GameStatus.WAITING_FOR_PLAYERS, nullable=False)
    current_turn = Column(Enum(PieceColor), default=PieceColor.WHITE, nullable=False)
    current_player_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player_white_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player_black_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    current_player = relationship("User", foreign_keys=[current_player_id], backref="current_games_playing")
    player_white = relationship("User", foreign_keys=[player_white_id], backref="games_as_white")
    player_black = relationship("User", foreign_keys=[player_black_id], backref="games_as_black")
    board = relationship("Board", back_populates="game", uselist=False, cascade="all, delete-orphan")


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), unique=True, nullable=False)
    state = Column(JSON, nullable=False) # Represents the 8x8 grid or variant grid
    last_move_san = Column(String, nullable=True) # Last move in Standard Algebraic Notation
    fen = Column(String, nullable=True) # Forsyth-Edwards Notation for board state
    # Special state flags (e.g., castling rights, en passant target, halfmove clock)
    castling_rights = Column(String, default="KQkq") # Example: "KQkq", "Kq"
    en_passant_target = Column(String, nullable=True) # Example: "e3"
    halfmove_clock = Column(Integer, default=0) # For 50-move rule
    fullmove_number = Column(Integer, default=1) # Increments after Black's move

    game = relationship("Game", back_populates="board")
    pieces = relationship("Piece", back_populates="board", cascade="all, delete-orphan")


class Piece(Base):
    __tablename__ = "pieces"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    piece_type = Column(String, nullable=False) # e.g., "Pawn", "Rook", "Knight", "King", "Queen", etc.
    color = Column(Enum(PieceColor), nullable=False)
    position_x = Column(Integer, nullable=False) # 0-indexed column (a=0, h=7)
    position_y = Column(Integer, nullable=False) # 0-indexed row (1=0, 8=7)
    is_captured = Column(Boolean, default=False)
    moved = Column(Boolean, default=False) # True if piece has moved at least once

    board = relationship("Board", back_populates="pieces")

    def to_dict(self):
        return {
            "id": self.id,
            "piece_type": self.piece_type,
            "color": self.color.value,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "is_captured": self.is_captured,
            "moved": self.moved
        }
