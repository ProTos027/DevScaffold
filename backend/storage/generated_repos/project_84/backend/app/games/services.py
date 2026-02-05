from typing import Tuple, List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.games.models import Game, Board, Piece, GameStatus, PieceColor
from app.core.exceptions import BadRequestException, NotFoundException


class PieceMovementService:
    """Handles custom piece movement rules for chess variants."""

    @staticmethod
    def get_legal_moves(board: Board, piece: Piece, game_rules: Dict[str, Any]) -> List[Tuple[int, int]]:
        """Calculates all legal moves for a given piece based on variant rules.
        This is a placeholder for complex chess variant logic.
        """
        # Example: Basic pawn movement for standard chess (very simplified)
        legal_moves = []
        board_grid = PieceMovementService._create_board_grid(board.pieces)

        if piece.piece_type == "Pawn":
            direction = 1 if piece.color == PieceColor.WHITE else -1
            start_row = 1 if piece.color == PieceColor.WHITE else 6

            # Single square forward
            if 0 <= piece.position_y + direction < 8 and board_grid[piece.position_x][piece.position_y + direction] is None:
                legal_moves.append((piece.position_x, piece.position_y + direction))

                # Double square forward from starting position
                if piece.position_y == start_row and board_grid[piece.position_x][piece.position_y + (2 * direction)] is None:
                    legal_moves.append((piece.position_x, piece.position_y + (2 * direction)))

            # Basic capture (diagonal)
            for dx in [-1, 1]:
                target_x, target_y = piece.position_x + dx, piece.position_y + direction
                if 0 <= target_x < 8 and 0 <= target_y < 8:
                    target_piece = board_grid[target_x][target_y]
                    if target_piece and target_piece.color != piece.color:
                        legal_moves.append((target_x, target_y))

            # TODO: Add en passant, promotion logic here

        # TODO: Implement logic for Rook, Knight, Bishop, Queen, King for standard chess and variants
        # This will involve checking for obstructions, valid target squares, special moves like castling.

        return legal_moves

    @staticmethod
    def is_move_legal(board: Board, piece: Piece, from_coords: Tuple[int, int], to_coords: Tuple[int, int], game_rules: Dict[str, Any]) -> bool:
        """Checks if a specific move is legal for a given piece and board state."""
        legal_moves = PieceMovementService.get_legal_moves(board, piece, game_rules)
        return to_coords in legal_moves

    @staticmethod
    def check_path_obstruction(board: Board, from_coords: Tuple[int, int], to_coords: Tuple[int, int]) -> bool:
        """Checks if there are any pieces obstructing a straight or diagonal path.
        Does not apply to knights.
        """
        # This would be a complex implementation based on geometry and piece type
        # For example, iterate squares between from_coords and to_coords
        return False # Placeholder

    @staticmethod
    def _create_board_grid(pieces: List[Piece]) -> List[List[Optional[Piece]]]:
        """Helper to convert a list of pieces into a 2D grid for easier lookup."""
        grid = [[None for _ in range(8)] for _ in range(8)]
        for piece in pieces:
            if not piece.is_captured:
                grid[piece.position_x][piece.position_y] = piece
        return grid


class BoardService:
    """Manages the game board state, including initialization, updates, and validation."""

    @staticmethod
    def initialize_board(game_id: int, variant_name: str = "Standard Chess") -> Board:
        """Initializes a new game board with pieces for standard chess or a variant."""
        board_state = [[' ' for _ in range(8)] for _ in range(8)] # Simplified 8x8 grid
        board = Board(
            game_id=game_id,
            state=board_state,
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            castling_rights="KQkq",
            en_passant_target=None,
            halfmove_clock=0,
            fullmove_number=1
        )

        # Standard Chess piece setup (example)
        piece_setup = [
            # Rooks
            ("Rook", PieceColor.WHITE, 0, 0), ("Rook", PieceColor.WHITE, 7, 0),
            ("Rook", PieceColor.BLACK, 0, 7), ("Rook", PieceColor.BLACK, 7, 7),
            # Knights
            ("Knight", PieceColor.WHITE, 1, 0), ("Knight", PieceColor.WHITE, 6, 0),
            ("Knight", PieceColor.BLACK, 1, 7), ("Knight", PieceColor.BLACK, 6, 7),
            # Bishops
            ("Bishop", PieceColor.WHITE, 2, 0), ("Bishop", PieceColor.WHITE, 5, 0),
            ("Bishop", PieceColor.BLACK, 2, 7), ("Bishop", PieceColor.BLACK, 5, 7),
            # Queens
            ("Queen", PieceColor.WHITE, 3, 0), ("Queen", PieceColor.BLACK, 3, 7),
            # Kings
            ("King", PieceColor.WHITE, 4, 0), ("King", PieceColor.BLACK, 4, 7),
        ]
        # Pawns
        for i in range(8):
            piece_setup.append(("Pawn", PieceColor.WHITE, i, 1))
            piece_setup.append(("Pawn", PieceColor.BLACK, i, 6))

        for p_type, p_color, x, y in piece_setup:
            board.pieces.append(Piece(piece_type=p_type, color=p_color, position_x=x, position_y=y))

        # TODO: Implement variant-specific board initialization here

        return board

    @staticmethod
    def update_board_after_move(db: Session, board: Board, moving_piece: Piece, from_coords: Tuple[int, int], to_coords: Tuple[int, int], promotion_choice: Optional[str] = None):
        """Applies a valid move to the board state and updates piece positions."""
        target_piece = db.query(Piece).filter(
            Piece.board_id == board.id,
            Piece.position_x == to_coords[0],
            Piece.position_y == to_coords[1],
            Piece.is_captured == False
        ).first()

        if target_piece:
            target_piece.is_captured = True
            db.add(target_piece)

        # Update moving piece's position and moved status
        moving_piece.position_x = to_coords[0]
        moving_piece.position_y = to_coords[1]
        moving_piece.moved = True
        db.add(moving_piece)

        # Handle promotion if applicable
        if promotion_choice and moving_piece.piece_type == "Pawn":
            promotion_rank = 7 if moving_piece.color == PieceColor.WHITE else 0
            if moving_piece.position_y == promotion_rank:
                moving_piece.piece_type = promotion_choice # e.g., 'Queen'
                db.add(moving_piece)

        # TODO: Update FEN, castling rights, en passant target, halfmove clock, fullmove number
        # For now, a simplified update:
        board.last_move_san = f"{chr(ord('a') + from_coords[0])}{from_coords[1]+1}-{chr(ord('a') + to_coords[0])}{to_coords[1]+1}"
        # Regenerate FEN (complex, often uses a library like python-chess)
        # For this boilerplate, we'll keep it simple or assume it's updated externally.

        db.add(board)
        db.commit()
        db.refresh(board)
        db.refresh(moving_piece)


    @staticmethod
    def validate_move_legality(db: Session, game: Game, from_coords: Tuple[int, int], to_coords: Tuple[int, int], promotion_choice: Optional[str] = None) -> Piece:
        """Validates a move's legality based on piece rules and board state."""
        board = game.board
        if not board:
            raise BadRequestException("Game board not initialized.")

        moving_piece = db.query(Piece).filter(
            Piece.board_id == board.id,
            Piece.position_x == from_coords[0],
            Piece.position_y == from_coords[1],
            Piece.is_captured == False
        ).first()

        if not moving_piece:
            raise BadRequestException("No piece found at the 'from' coordinates.")

        if moving_piece.color != game.current_turn:
            raise BadRequestException(f"It's {game.current_turn.value}'s turn, but a {moving_piece.color.value} piece was moved.")

        game_rules = {"variant": game.variant_name} # Placeholder for actual rules config
        if not PieceMovementService.is_move_legal(board, moving_piece, from_coords, to_coords, game_rules):
            raise BadRequestException("Illegal move according to piece rules or board state.")

        # TODO: Add checks for: leaving king in check, castling rules, en passant validity, etc.

        return moving_piece

    @staticmethod
    def determine_game_state(db: Session, game: Game):
        """Determines if the game is in check, checkmate, stalemate, etc."""
        # This is a very complex logic requiring simulating moves, checking for king attacks.
        # For boilerplate, we'll just toggle the turn.

        # Placeholder: Check for simple check/mate conditions (not implemented)
        # For now, simply update turn.
        pass


class GameService:
    """Manages game instances, progression, and state updates."""

    @staticmethod
    def create_game(db: Session, title: str, variant_name: str, player_white_id: int) -> Game:
        """Creates a new game instance and initializes its board."""
        new_game = Game(
            title=title,
            variant_name=variant_name,
            player_white_id=player_white_id,
            status=GameStatus.WAITING_FOR_PLAYERS,
            current_turn=PieceColor.WHITE # White always starts
        )
        db.add(new_game)
        db.commit()
        db.refresh(new_game)

        new_board = BoardService.initialize_board(new_game.id, variant_name)
        db.add(new_board)
        db.commit()
        db.refresh(new_game) # Refresh game to load board relationship
        return new_game

    @staticmethod
    def get_game_by_id(db: Session, game_id: int) -> Optional[Game]:
        """Retrieves a game instance by its ID."""
        return db.query(Game).filter(Game.id == game_id).first()

    @staticmethod
    def apply_move(db: Session, game: Game, player_id: int, from_coords: Tuple[int, int], to_coords: Tuple[int, int], promotion_choice: Optional[str] = None) -> Game:
        """Applies a move to the game, updates the board, and progresses the game state."""
        # 1. Validate move legality (piece rules, board state, check, etc.)
        moving_piece = BoardService.validate_move_legality(db, game, from_coords, to_coords, promotion_choice)

        # 2. Update board state with the move
        BoardService.update_board_after_move(db, game.board, moving_piece, from_coords, to_coords, promotion_choice)

        # 3. Determine new game state (check, checkmate, stalemate, draw)
        # For now, just switch turns
        game.current_turn = PieceColor.BLACK if game.current_turn == PieceColor.WHITE else PieceColor.WHITE

        # Update current_player_id based on new turn
        if game.current_turn == PieceColor.WHITE:
            game.current_player_id = game.player_white_id
        else:
            game.current_player_id = game.player_black_id

        # Placeholder: If a complex game state logic was implemented in BoardService.determine_game_state,
        # it would update game.status here.
        # Example:
        # game_status_update = BoardService.determine_game_state(db, game)
        # if game_status_update:
        #    game.status = game_status_update

        db.add(game)
        db.commit()
        db.refresh(game)

        return game
