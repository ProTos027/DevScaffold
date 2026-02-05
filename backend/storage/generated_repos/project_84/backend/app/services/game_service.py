from typing import List, Optional, Dict
import uuid
from enum import Enum

from pydantic import BaseModel, Field

# --- Placeholder Models (Ideally imported from app.models) ---

class User(BaseModel):
    id: str
    username: str

class PieceType(str, Enum):
    X = "X"
    O = "O"

class Piece(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: PieceType
    owner_id: str

# For a simple 3x3 tic-tac-toe like board
class Board(BaseModel):
    cells: List[List[Optional[PieceType]]] = Field(
        default_factory=lambda: [[None, None, None], [None, None, None], [None, None, None]]
    )

class GameStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DRAW = "DRAW"

class Move(BaseModel):
    player_id: str
    row: int
    col: int

class Game(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player1_id: str
    player2_id: str
    current_player_id: str
    board: Board = Field(default_factory=Board)
    status: GameStatus = GameStatus.IN_PROGRESS
    winner_id: Optional[str] = None
    move_history: List[Move] = Field(default_factory=list)
    player1_piece_type: PieceType
    player2_piece_type: PieceType

# --- Custom Exceptions ---
class GameNotFoundException(Exception):
    def __init__(self, game_id: str):
        super().__init__(f"Game with ID '{game_id}' not found.")

class InvalidMoveException(Exception):
    pass

class NotPlayersTurnException(InvalidMoveException):
    def __init__(self, player_id: str, current_player_id: str):
        super().__init__(f"It's not player {player_id}'s turn. Current player is {current_player_id}.")

class GameOverException(InvalidMoveException):
    def __init__(self, game_id: str, status: GameStatus):
        super().__init__(f"Game {game_id} is already {status.value}.")

class GameService:
    """Service to manage game instances, progression, and state updates."""

    def __init__(self):
        # In-memory store for game instances for demonstration purposes
        self.games: Dict[str, Game] = {}

    def _get_piece_type_for_player(self, game: Game, player_id: str) -> PieceType:
        if game.player1_id == player_id:
            return game.player1_piece_type
        elif game.player2_id == player_id:
            return game.player2_piece_type
        raise ValueError(f"Player {player_id} is not part of this game.")

    def _check_win(self, board: Board, player_piece_type: PieceType) -> bool:
        # Check rows, columns, and diagonals for a win (3x3 tic-tac-toe logic)
        cells = board.cells
        # Check rows
        for row in cells:
            if all(cell == player_piece_type for cell in row):
                return True
        # Check columns
        for col_idx in range(3):
            if all(cells[row_idx][col_idx] == player_piece_type for row_idx in range(3)):
                return True
        # Check diagonals
        if all(cells[i][i] == player_piece_type for i in range(3)) or \
           all(cells[i][2 - i] == player_piece_type for i in range(3)):
            return True
        return False

    def _check_draw(self, board: Board) -> bool:
        # Check if all cells are filled (for 3x3 tic-tac-toe)
        return all(cell is not None for row in board.cells for cell in row)

    def create_game(self, player1_id: str, player2_id: str) -> Game:
        """Creates a new game instance between two players."""
        if player1_id == player2_id:
            raise InvalidMoveException("Players must be different.")

        game_id = str(uuid.uuid4())
        # Player 1 gets 'X', Player 2 gets 'O'
        new_game = Game(
            id=game_id,
            player1_id=player1_id,
            player2_id=player2_id,
            current_player_id=player1_id, # Player 1 starts
            status=GameStatus.IN_PROGRESS,
            player1_piece_type=PieceType.X,
            player2_piece_type=PieceType.O
        )
        self.games[game_id] = new_game
        return new_game

    def get_game(self, game_id: str) -> Game:
        """Retrieves a specific game instance by its ID."""
        game = self.games.get(game_id)
        if not game:
            raise GameNotFoundException(game_id)
        return game

    def make_move(self, game_id: str, player_id: str, move_data: Move) -> Game:
        """Applies a move to the game state and updates the game status."""
        game = self.get_game(game_id)

        if game.status != GameStatus.IN_PROGRESS:
            raise GameOverException(game_id, game.status)

        if game.current_player_id != player_id:
            raise NotPlayersTurnException(player_id, game.current_player_id)

        # Validate move coordinates
        row, col = move_data.row, move_data.col
        if not (0 <= row < 3 and 0 <= col < 3):
            raise InvalidMoveException(f"Move ({row},{col}) is out of board bounds.")

        # Check if cell is already occupied
        if game.board.cells[row][col] is not None:
            raise InvalidMoveException(f"Cell ({row},{col}) is already occupied.")

        # Get the piece type for the current player
        player_piece_type = self._get_piece_type_for_player(game, player_id)

        # Apply the move
        game.board.cells[row][col] = player_piece_type
        game.move_history.append(move_data) # Add move to history

        # Check for win condition
        if self._check_win(game.board, player_piece_type):
            game.status = GameStatus.COMPLETED
            game.winner_id = player_id
        # Check for draw condition
        elif self._check_draw(game.board):
            game.status = GameStatus.DRAW
        else:
            # Switch turn to the other player
            game.current_player_id = game.player2_id if player_id == game.player1_id else game.player1_id

        self.games[game_id] = game # Update the game in storage
        return game
