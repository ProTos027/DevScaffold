import uuid
from typing import Dict, List, Optional
from enum import Enum

# NOTE: In a real application, these models and services would be imported
# from their respective modules (e.g., app.models.game, app.models.user, app.services.game_logic_service).
# For the purpose of this self-contained response, minimal mock implementations are provided here.

# --- Mock Models (Simulating app/models/game.py and app/models/user.py) ---
class GameStatus(str, Enum):
    WAITING_FOR_PLAYER = "WAITING_FOR_PLAYER"
    IN_PROGRESS = "IN_PROGRESS"
    PLAYER1_WON = "PLAYER1_WON"
    PLAYER2_WON = "PLAYER2_WON"
    DRAW = "DRAW"
    TERMINATED = "TERMINATED"

class Piece:
    def __init__(self, color: str, type: str, position: str):
        self.color = color
        self.type = type
        self.position = position # e.g., "a1"

    def to_dict(self):
        return {"color": self.color, "type": self.type, "position": self.position}

class BoardState:
    def __init__(self):
        # Example: A dictionary mapping board positions (e.g., "a1") to Piece objects
        self.board: Dict[str, Optional[Piece]] = {}
        self.turn: str = "player1" # Tracks whose 'color' pieces are to move next
        self.last_move: Optional[Dict] = None

    def to_dict(self):
        return {
            "board": {pos: piece.to_dict() for pos, piece in self.board.items() if piece},
            "turn": self.turn,
            "last_move": self.last_move
        }

class Game:
    def __init__(self, game_id: str, player1_id: str):
        self.game_id: str = game_id
        self.player1_id: str = player1_id
        self.player2_id: Optional[str] = None
        self.status: GameStatus = GameStatus.WAITING_FOR_PLAYER
        self.board_state: BoardState = BoardState()
        self.current_turn_player_id: str = player1_id # ID of the player whose turn it is
        self.move_history: List[Dict] = [] # Stores validated move data after application
        self.winner_id: Optional[str] = None
        self.created_at: str = str(uuid.uuid4()) # Placeholder for timestamp
        self.updated_at: str = str(uuid.uuid4()) # Placeholder for timestamp

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "status": self.status.value,
            "board_state": self.board_state.to_dict(),
            "current_turn_player_id": self.current_turn_player_id,
            "move_history": self.move_history,
            "winner_id": self.winner_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

User = str # Mock User model: simply represented by a string ID

# --- Mock Game Logic Service (Simulating app/services/game_logic_service.py) ---
class GameLogicService:
    def validate_move(self, game: Game, player_id: str, move_data: Dict) -> bool:
        """
        Validates if a move is legal given the current game state and player.
        In a real game, this would contain complex rules (e.g., chess rules, turn validation).
        """
        if game.current_turn_player_id != player_id:
            # print(f"DEBUG: Not player {player_id}'s turn. Current: {game.current_turn_player_id}")
            return False

        required_keys = ["from_position", "to_position"]
        if not all(key in move_data for key in required_keys):
            # print(f"DEBUG: Missing required move_data keys. {move_data}")
            return False

        from_pos = move_data["from_position"]
        piece_on_board = game.board_state.board.get(from_pos)
        if not piece_on_board:
            # print(f"DEBUG: No piece at {from_pos}.")
            return False

        # Assume player1 uses 'white' pieces and player2 uses 'black'
        expected_color = "white" if game.player1_id == player_id else "black"
        if piece_on_board.color != expected_color:
            # print(f"DEBUG: Piece at {from_pos} belongs to opponent.")
            return False

        # More complex validation (e.g., path clear, piece specific movement) would go here.
        return True

    def apply_move(self, game: Game, player_id: str, move_data: Dict) -> None:
        """
        Applies a validated move to the game's board state. Updates piece positions.
        """
        from_pos = move_data["from_position"]
        to_pos = move_data["to_position"]

        piece = game.board_state.board.pop(from_pos) # Remove piece from old position
        if piece:
            piece.position = to_pos # Update the piece's internal position
            game.board_state.board[to_pos] = piece # Place piece at new position

        game.board_state.last_move = {
            "player_id": player_id,
            "from": from_pos,
            "to": to_pos,
            "piece_type": piece.type if piece else None,
            "timestamp": str(uuid.uuid4()) # Placeholder timestamp
        }

    def check_game_over(self, game: Game) -> Optional[GameStatus]:
        """
        Checks if the game has ended due to a win, loss, or draw condition.
        Returns the GameStatus if over, otherwise None.
        """
        # Placeholder logic: Simulate game end after a few moves for demonstration.
        if len(game.move_history) >= 5 and game.player1_id.startswith("test_"):
            return GameStatus.PLAYER1_WON
        if len(game.move_history) >= 7 and game.player2_id and game.player2_id.startswith("test_"):
            return GameStatus.PLAYER2_WON
        if len(game.move_history) > 10:
            return GameStatus.DRAW
        return None

# --- Game Service Implementation ---
class GameService:
    def __init__(self):
        # In-memory storage for active games. In a real application, this would be a database client.
        self.games: Dict[str, Game] = {}
        self.game_logic_service = GameLogicService() # Dependency injection could be used here

    def create_game(self, player1_id: str) -> Game:
        """
        Creates a new game instance, assigning the first player and initializing the board.
        """
        game_id = str(uuid.uuid4())
        game = Game(game_id=game_id, player1_id=player1_id)

        # Initialize a basic board state (e.g., for a 2-piece game)
        game.board_state.board["a1"] = Piece("white", "pawn", "a1")
        game.board_state.board["b1"] = Piece("white", "pawn", "b1")
        game.board_state.board["a8"] = Piece("black", "pawn", "a8")
        game.board_state.board["b8"] = Piece("black", "pawn", "b8")
        game.board_state.turn = "player1" # Player1 (white) starts

        self.games[game_id] = game
        return game

    def join_game(self, game_id: str, player2_id: str) -> Game:
        """
        Allows a second player to join an existing game that is awaiting players.
        """
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with ID {game_id} not found.")

        if game.status != GameStatus.WAITING_FOR_PLAYER:
            raise ValueError(f"Game {game_id} is not waiting for a second player. Current status: {game.status.value}")

        if game.player1_id == player2_id:
            raise ValueError(f"Player {player2_id} is already Player 1 in this game.")

        game.player2_id = player2_id
        game.status = GameStatus.IN_PROGRESS
        game.current_turn_player_id = game.player1_id # Player 1 always starts
        game.updated_at = str(uuid.uuid4())
        self.games[game_id] = game
        return game

    def make_move(self, game_id: str, player_id: str, move_data: Dict) -> Game:
        """
        Processes a player's move, validates it, updates the game state, and checks for game over conditions.
        """
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with ID {game_id} not found.")

        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError(f"Cannot make move. Game {game_id} is not IN_PROGRESS. Status: {game.status.value}")

        if game.current_turn_player_id != player_id:
            raise ValueError(f"It is not player {player_id}'s turn. Current turn: {game.current_turn_player_id}")

        if not self.game_logic_service.validate_move(game, player_id, move_data):
            raise ValueError(f"Invalid move for game {game_id}, player {player_id}: {move_data}")

        self.game_logic_service.apply_move(game, player_id, move_data)
        game.move_history.append(game.board_state.last_move)

        game_over_status = self.game_logic_service.check_game_over(game)
        if game_over_status:
            game.status = game_over_status
            if game_over_status == GameStatus.PLAYER1_WON:
                game.winner_id = game.player1_id
            elif game_over_status == GameStatus.PLAYER2_WON:
                game.winner_id = game.player2_id
        else:
            # Switch turns
            if game.player1_id == player_id:
                game.current_turn_player_id = game.player2_id
            else:
                game.current_turn_player_id = game.player1_id
        
        game.updated_at = str(uuid.uuid4())
        self.games[game_id] = game

        # NOTE: In a real-time multiplayer scenario, this would trigger a WebSocket update
        # to notify all connected clients about the game state change.
        return game

    def get_game_state(self, game_id: str) -> Game:
        """
        Retrieves the current state of a specific game.
        """
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with ID {game_id} not found.")
        return game

    def get_game_history(self, game_id: str) -> List[Dict]:
        """
        Retrieves the full move history of a specific game.
        """
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with ID {game_id} not found.")
        return game.move_history

    def terminate_game(self, game_id: str, initiator_id: str) -> Game:
        """
        Terminates a game. This can be initiated by a player or an admin.
        """
        game = self.games.get(game_id)
        if not game:
            raise ValueError(f"Game with ID {game_id} not found.")

        # Optional: Add authorization check
        if initiator_id not in [game.player1_id, game.player2_id] and initiator_id != "admin_user":
            raise ValueError(f"Player {initiator_id} is not authorized to terminate game {game_id}.")

        game.status = GameStatus.TERMINATED
        game.updated_at = str(uuid.uuid4())
        self.games[game_id] = game
        return game
