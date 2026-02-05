from typing import List, Optional, Tuple, Set
import copy
from enum import Enum

# --- Data Models (as per instructions, assuming they are defined in app/models/chess.py or similar) ---
# For self-containment and demonstration, they are defined here. In a real project,
# these would be in 'app/models/chess.py' and imported.

class PieceType(str, Enum):
    PAWN = "P"
    KNIGHT = "N"
    BISHOP = "B"
    ROOK = "R"
    QUEEN = "Q"
    KING = "K"

class Color(str, Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"

class Piece:
    def __init__(self, type: PieceType, color: Color):
        self.type = type
        self.color = color

    def __repr__(self):
        return f"Piece({self.color.value[0]}{self.type.value})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return NotImplemented
        return self.type == other.type and self.color == other.color

    def __hash__(self):
        return hash((self.type, self.color))

class Move:
    def __init__(self, start_row: int, start_col: int, end_row: int, end_col: int, promotion_piece_type: Optional[PieceType] = None):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.promotion_piece_type = promotion_piece_type

    def __repr__(self):
        promo = f" (promo: {self.promotion_piece_type.value})" if self.promotion_piece_type else ""
        return f"Move({self.start_row},{self.start_col})->({self.end_row},{self.end_col}){promo}"

    def __eq__(self, other):
        if not isinstance(other, Move):
            return NotImplemented
        return (self.start_row == other.start_row and
                self.start_col == other.start_col and
                self.end_row == other.end_row and
                self.end_col == other.end_col and
                self.promotion_piece_type == other.promotion_piece_type)

    def __hash__(self):
        return hash((self.start_row, self.start_col, self.end_row, self.end_col, self.promotion_piece_type))

class GameStatus(str, Enum):
    ONGOING = "ONGOING"
    CHECK = "CHECK"
    CHECKMATE = "CHECKMATE"
    STALEMATE = "STALEMATE"
    DRAW_FIFTY_MOVE = "DRAW_FIFTY_MOVE"
    DRAW_THREEFOLD_REPETITION = "DRAW_THREEFOLD_REPETITION"
    DRAW_INSUFFICIENT_MATERIAL = "DRAW_INSUFFICIENT_MATERIAL"

class Board:
    def __init__(self):
        # 8x8 grid of Optional[Piece] representing the board state
        self._board_state: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.turn: Color = Color.WHITE
        self.castling_rights: str = "KQkq" # FEN notation for castling rights
        self.en_passant_target: Optional[Tuple[int, int]] = None # (row, col) of the target square
        self.halfmove_clock: int = 0 # Number of halfmoves since the last capture or pawn advance, for fifty-move rule
        self.fullmove_number: int = 1 # Number of full moves, starting at 1, incremented after Black's move
        self.history: List[str] = [] # List of FEN strings for threefold repetition detection
        self.current_fen: str = "" # Stores the FEN string representation of the current board state

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < 8 and 0 <= col < 8:
            return self._board_state[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        if 0 <= row < 8 and 0 <= col < 8:
            self._board_state[row][col] = piece

    def clone(self) -> 'Board':
        new_board = Board()
        new_board.turn = self.turn
        new_board.castling_rights = self.castling_rights
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.history = list(self.history) # Shallow copy of history list
        new_board.current_fen = self.current_fen
        # Deep copy board state (Piece objects are immutable, so shallow copy of references is fine)
        for r in range(8):
            for c in range(8):
                new_board._board_state[r][c] = self._board_state[r][c]
        return new_board

    def to_fen_position_only(self) -> str:
        """Generates the board position part of the FEN string."""
        fen_parts = []
        for r in range(8):
            empty_count = 0
            row_fen = []
            for c in range(8):
                piece = self._board_state[r][c]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_fen.append(str(empty_count))
                        empty_count = 0
                    char = piece.type.value
                    if piece.color == Color.BLACK:
                        char = char.lower()
                    row_fen.append(char)
            if empty_count > 0:
                row_fen.append(str(empty_count))
            fen_parts.append("".join(row_fen))
        return "/".join(fen_parts)

    def to_fen(self) -> str:
        """Generates the full FEN string from current board state."""
        position_part = self.to_fen_position_only()
        active_color_part = 'w' if self.turn == Color.WHITE else 'b'
        castling_part = self.castling_rights if self.castling_rights else '-'
        
        en_passant_part = '-'
        if self.en_passant_target:
            row, col = self.en_passant_target
            # Convert (row, col) to algebraic notation, e.g., (2,4) -> e6
            en_passant_part = f"{chr(ord('a') + col)}{8 - row}"

        return f"{position_part} {active_color_part} {castling_part} {en_passant_part} {self.halfmove_clock} {self.fullmove_number}"

    def update_from_fen(self, fen: str):
        """Updates the board state based on a FEN string."""
        parts = fen.split(' ')
        
        # Position part
        board_rows = parts[0].split('/')
        for r_idx, row_str in enumerate(board_rows):
            c_idx = 0
            for char in row_str:
                if char.isdigit():
                    c_idx += int(char)
                else:
                    color = Color.WHITE if char.isupper() else Color.BLACK
                    piece_type = PieceType(char.upper())
                    self.set_piece(r_idx, c_idx, Piece(piece_type, color))
                    c_idx += 1
        
        # Active color
        self.turn = Color.WHITE if parts[1] == 'w' else Color.BLACK
        
        # Castling rights
        self.castling_rights = parts[2]
        
        # En passant target square
        en_passant_square = parts[3]
        if en_passant_square != '-':
            col = ord(en_passant_square[0]) - ord('a')
            row = 8 - int(en_passant_square[1]) # Convert '1' to row 7, '8' to row 0
            self.en_passant_target = (row, col)
        else:
            self.en_passant_target = None
            
        # Halfmove clock
        self.halfmove_clock = int(parts[4])
        
        # Fullmove number
        self.fullmove_number = int(parts[5])
        
        # Update current FEN and history
        self.current_fen = fen
        self.history.append(fen)


class BoardService:
    def __init__(self):
        # BoardService is stateless, operating on Board objects passed to its methods.
        pass

    def initialize_board(self) -> Board:
        """Initializes a new game board to the standard starting configuration."""
        board = Board()
        # Standard chess starting position in FEN notation
        initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board.update_from_fen(initial_fen)
        return board

    def _is_square_attacked(self, board: Board, target_row: int, target_col: int, attacking_color: Color) -> bool:
        """Checks if a given square is attacked by any piece of the `attacking_color`."""
        
        # Directions for sliding pieces
        STRAIGHT_DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Rook, Queen
        DIAGONAL_DIRECTIONS = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Bishop, Queen

        # Knight moves
        KNIGHT_MOVES = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        # King moves (for checking opponent's king proximity)
        KING_MOVES = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        # Pawn attacks
        pawn_attack_dirs = []
        if attacking_color == Color.WHITE: # White pawns attack diagonally up (decreasing row)
            pawn_attack_dirs = [(-1, -1), (-1, 1)]
        else: # Black pawns attack diagonally down (increasing row)
            pawn_attack_dirs = [(1, -1), (1, 1)]

        # Check for pawn attacks
        for dr, dc in pawn_attack_dirs:
            r, c = target_row + dr, target_col + dc
            piece = board.get_piece(r, c)
            if piece and piece.color == attacking_color and piece.type == PieceType.PAWN:
                return True

        # Check for knight attacks
        for dr, dc in KNIGHT_MOVES:
            r, c = target_row + dr, target_col + dc
            piece = board.get_piece(r, c)
            if piece and piece.color == attacking_color and piece.type == PieceType.KNIGHT:
                return True

        # Check for sliding piece attacks (Rook, Bishop, Queen)
        # Combine directions for efficiency
        # STRAIGHT_DIRECTIONS for Rook/Queen
        # DIAGONAL_DIRECTIONS for Bishop/Queen
        for dr, dc in STRAIGHT_DIRECTIONS + DIAGONAL_DIRECTIONS:
            for i in range(1, 8):
                r, c = target_row + dr * i, target_col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break # Out of bounds
                
                piece = board.get_piece(r, c)
                if piece:
                    if piece.color == attacking_color:
                        if piece.type == PieceType.QUEEN: return True
                        if piece.type == PieceType.ROOK and (dr == 0 or dc == 0): return True # Straight line of sight
                        if piece.type == PieceType.BISHOP and (dr != 0 and dc != 0): return True # Diagonal line of sight
                    break # Path is blocked by any piece (own or opponent's)
        
        # Check for opponent's king (to prevent moving king next to opponent's king)
        for dr, dc in KING_MOVES:
            r, c = target_row + dr, target_col + dc
            piece = board.get_piece(r, c)
            if piece and piece.color == attacking_color and piece.type == PieceType.KING:
                return True

        return False

    def _find_king_position(self, board: Board, color: Color) -> Optional[Tuple[int, int]]:
        """Finds the current position of the king of a given color."""
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece and piece.type == PieceType.KING and piece.color == color:
                    return (r, c)
        return None # Should ideally not happen in a valid game state unless king is captured

    def _is_king_in_check(self, board: Board, king_color: Color) -> bool:
        """Determines if the king of `king_color` is currently in check."""
        king_pos = self._find_king_position(board, king_color)
        if not king_pos:
            return False # King missing, invalid state
        
        opponent_color = Color.WHITE if king_color == Color.BLACK else Color.BLACK
        return self._is_square_attacked(board, king_pos[0], king_pos[1], opponent_color)

    def is_move_legal(self, board: Board, move: Move) -> bool:
        """Validates if a given move is legal according to chess rules."""
        start_row, start_col = move.start_row, move.start_col
        end_row, end_col = move.end_row, move.end_col
        
        # 1. Basic boundary and piece existence/ownership checks
        if not (0 <= start_row < 8 and 0 <= start_col < 8 and 0 <= end_row < 8 and 0 <= end_col < 8):
            return False # Move out of bounds
        
        piece = board.get_piece(start_row, start_col)
        if not piece or piece.color != board.turn:
            return False # No piece at start, or not current player's piece
        
        target_piece = board.get_piece(end_row, end_col)
        if target_piece and target_piece.color == board.turn:
            return False # Cannot capture your own piece

        # Prevent moving to the same square (unless it's a null move in FEN, but not supported here)
        if start_row == end_row and start_col == end_col: 
            return False

        # 2. Piece-specific movement rules and obstruction checks
        is_valid_piece_move = False
        
        dr = end_row - start_row
        dc = end_col - start_col
        abs_dr = abs(dr)
        abs_dc = abs(dc)

        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1 # White moves up (decreasing row), Black down (increasing row)
            start_rank = 6 if piece.color == Color.WHITE else 1 # White starts on rank 2 (row 6), Black on rank 7 (row 1)
            
            # Normal one-step move
            if dc == 0 and dr == direction and target_piece is None:
                is_valid_piece_move = True
            # Two-step initial move
            elif dc == 0 and dr == 2 * direction and target_piece is None and 
                 start_row == start_rank and 
                 board.get_piece(start_row + direction, start_col) is None: # Check intermediate square is empty
                is_valid_piece_move = True
            # Normal capture
            elif abs_dc == 1 and dr == direction and target_piece and target_piece.color != piece.color:
                is_valid_piece_move = True
            # En passant capture
            elif abs_dc == 1 and dr == direction and target_piece is None:
                if board.en_passant_target == (end_row, end_col): # Target square must be the en passant square
                    # The piece to be captured is the opponent's pawn at (start_row, end_col)
                    captured_pawn_row = start_row
                    captured_pawn_col = end_col
                    captured_pawn = board.get_piece(captured_pawn_row, captured_pawn_col)
                    if captured_pawn and captured_pawn.type == PieceType.PAWN and captured_pawn.color != piece.color:
                        is_valid_piece_move = True
            
            # Promotion check for pawn moves
            if is_valid_piece_move and (end_row == 0 or end_row == 7): # Reached last rank
                if not move.promotion_piece_type or 
                   move.promotion_piece_type in [PieceType.PAWN, PieceType.KING]:
                    # Invalid promotion piece or missing promotion type when required
                    return False 
            elif move.promotion_piece_type:
                # Cannot promote if not on last rank
                return False

        elif piece.type == PieceType.KNIGHT:
            if (abs_dr == 2 and abs_dc == 1) or (abs_dr == 1 and abs_dc == 2):
                is_valid_piece_move = True

        elif piece.type == PieceType.BISHOP:
            if abs_dr == abs_dc and abs_dr > 0: # Diagonal move
                is_valid_piece_move = True
                # Check for obstructions along the diagonal path
                step_dr = 1 if dr > 0 else -1
                step_dc = 1 if dc > 0 else -1
                for i in range(1, abs_dr):
                    if board.get_piece(start_row + i * step_dr, start_col + i * step_dc) is not None:
                        is_valid_piece_move = False
                        break

        elif piece.type == PieceType.ROOK:
            if (dr == 0 and abs_dc > 0) or (dc == 0 and abs_dr > 0): # Straight move (horizontal or vertical)
                is_valid_piece_move = True
                # Check for obstructions along the straight path
                if dr == 0: # Horizontal
                    step_dc = 1 if dc > 0 else -1
                    for i in range(1, abs_dc):
                        if board.get_piece(start_row, start_col + i * step_dc) is not None:
                            is_valid_piece_move = False
                            break
                else: # Vertical
                    step_dr = 1 if dr > 0 else -1
                    for i in range(1, abs_dr):
                        if board.get_piece(start_row + i * step_dr, start_col) is not None:
                            is_valid_piece_move = False
                            break

        elif piece.type == PieceType.QUEEN:
            if (abs_dr == abs_dc and abs_dr > 0) or \
               ((dr == 0 and abs_dc > 0) or (dc == 0 and abs_dr > 0)): # Diagonal or Straight
                is_valid_piece_move = True
                # Check for obstructions (same logic as bishop or rook)
                if abs_dr == abs_dc: # Diagonal
                    step_dr = 1 if dr > 0 else -1
                    step_dc = 1 if dc > 0 else -1
                    for i in range(1, abs_dr):
                        if board.get_piece(start_row + i * step_dr, start_col + i * step_dc) is not None:
                            is_valid_piece_move = False
                            break
                else: # Straight
                    if dr == 0: # Horizontal
                        step_dc = 1 if dc > 0 else -1
                        for i in range(1, abs_dc):
                            if board.get_piece(start_row, start_col + i * step_dc) is not None:
                                is_valid_piece_move = False
                                break
                    else: # Vertical
                        step_dr = 1 if dr > 0 else -1
                        for i in range(1, abs_dr):
                            if board.get_piece(start_row + i * step_dr, start_col) is not None:
                                is_valid_piece_move = False
                                break

        elif piece.type == PieceType.KING:
            if abs_dr <= 1 and abs_dc <= 1 and (abs_dr + abs_dc > 0): # One square in any direction
                is_valid_piece_move = True
            # Castling (King moves two squares horizontally)
            elif dr == 0 and abs_dc == 2: 
                king_start_row = 7 if piece.color == Color.WHITE else 0
                king_start_col = 4 # King's initial column

                if start_row != king_start_row or start_col != king_start_col: return False # King must be on starting square
                if self._is_king_in_check(board, piece.color): return False # Cannot castle out of check

                if dc == 2: # Kingside castling (O-O)
                    # Check castling rights and rook position
                    if (piece.color == Color.WHITE and 'K' not in board.castling_rights) or \
                       (piece.color == Color.BLACK and 'k' not in board.castling_rights): return False
                    rook = board.get_piece(king_start_row, 7)
                    if not (rook and rook.type == PieceType.ROOK and rook.color == piece.color): return False
                    # Check for obstructions between king and rook
                    if board.get_piece(king_start_row, 5) is not None or board.get_piece(king_start_row, 6) is not None: return False
                    # Check squares king passes through or lands on are not attacked
                    if self._is_square_attacked(board, king_start_row, 5, board.turn.BLACK if board.turn == Color.WHITE else Color.WHITE) or \
                       self._is_square_attacked(board, king_start_row, 6, board.turn.BLACK if board.turn == Color.WHITE else Color.WHITE): return False
                    is_valid_piece_move = True

                elif dc == -2: # Queenside castling (O-O-O)
                    # Check castling rights and rook position
                    if (piece.color == Color.WHITE and 'Q' not in board.castling_rights) or \
                       (piece.color == Color.BLACK and 'q' not in board.castling_rights): return False
                    rook = board.get_piece(king_start_row, 0)
                    if not (rook and rook.type == PieceType.ROOK and rook.color == piece.color): return False
                    # Check for obstructions between king and rook
                    if board.get_piece(king_start_row, 1) is not None or board.get_piece(king_start_row, 2) is not None or board.get_piece(king_start_row, 3) is not None: return False
                    # Check squares king passes through or lands on are not attacked
                    if self._is_square_attacked(board, king_start_row, 3, board.turn.BLACK if board.turn == Color.WHITE else Color.WHITE) or \
                       self._is_square_attacked(board, king_start_row, 2, board.turn.BLACK if board.turn == Color.WHITE else Color.WHITE): return False
                    is_valid_piece_move = True
        
        if not is_valid_piece_move:
            return False

        # 3. King safety check: Must not leave own king in check after the move
        temp_board = board.clone()
        # Apply the move to a temporary board without further legality checks
        # Need to explicitly pass if it's a castling move so rook moves correctly
        is_castling_move = (piece.type == PieceType.KING and abs_dc == 2)
        self._apply_move_internal(temp_board, move, is_castling=is_castling_move)
        
        if self._is_king_in_check(temp_board, piece.color):
            return False # Move leaves king in check, so it's illegal

        return True

    def _apply_move_internal(self, board: Board, move: Move, is_castling: bool = False):
        """Applies a move to the board directly without legality checks. Used for temporary boards."""
        start_row, start_col = move.start_row, move.start_col
        end_row, end_col = move.end_row, move.end_col

        moving_piece = board.get_piece(start_row, start_col)
        if not moving_piece: # Should not happen if called from a legal move context
            return
        
        # Handle en passant capture: if pawn moves diagonally to empty square, it must be en passant
        if moving_piece.type == PieceType.PAWN and abs(end_col - start_col) == 1 and board.get_piece(end_row, end_col) is None:
            # The captured pawn is on the start_row but end_col
            captured_pawn_row = start_row
            captured_pawn_col = end_col
            board.set_piece(captured_pawn_row, captured_pawn_col, None)

        # Move the piece
        board.set_piece(end_row, end_col, moving_piece)
        board.set_piece(start_row, start_col, None)

        # Handle pawn promotion
        if moving_piece.type == PieceType.PAWN and (end_row == 0 or end_row == 7) and move.promotion_piece_type:
            board.set_piece(end_row, end_col, Piece(move.promotion_piece_type, moving_piece.color))

        # Handle castling (move the rook)
        if is_castling:
            king_row = 7 if moving_piece.color == Color.WHITE else 0
            if end_col == 6: # Kingside castling (O-O) - move rook from 7 to 5
                rook = board.get_piece(king_row, 7)
                board.set_piece(king_row, 5, rook)
                board.set_piece(king_row, 7, None)
            elif end_col == 2: # Queenside castling (O-O-O) - move rook from 0 to 3
                rook = board.get_piece(king_row, 0)
                board.set_piece(king_row, 3, rook)
                board.set_piece(king_row, 0, None)

    def apply_move(self, board: Board, move: Move) -> Board:
        """Applies a valid move to the board and updates all game state variables."""
        if not self.is_move_legal(board, move):
            raise ValueError("Illegal move attempted")

        new_board = board.clone()
        start_row, start_col = move.start_row, move.start_col
        end_row, end_col = move.end_row, move.end_col
        
        moving_piece = new_board.get_piece(start_row, start_col)
        if not moving_piece: # Should be caught by is_move_legal, but defensive check
            raise ValueError("No piece found at start position for a legal move.")

        # Update halfmove clock
        # Reset if pawn move or capture
        is_capture = new_board.get_piece(end_row, end_col) is not None or \
                     (moving_piece.type == PieceType.PAWN and abs(end_col - start_col) == 1 and new_board.en_passant_target == (end_row, end_col))
        if moving_piece.type == PieceType.PAWN or is_capture:
            new_board.halfmove_clock = 0 
        else:
            new_board.halfmove_clock += 1 

        # Determine if castling for internal move application
        is_castling_move = (moving_piece.type == PieceType.KING and abs(end_col - start_col) == 2)
        
        # Apply the move to the new board state
        self._apply_move_internal(new_board, move, is_castling=is_castling_move)

        # Update en passant target square
        new_board.en_passant_target = None # Reset by default
        if moving_piece.type == PieceType.PAWN and abs(end_row - start_row) == 2: # If pawn moved two squares
            # The en passant target square is directly behind the pawn's destination
            new_board.en_passant_target = (start_row + (end_row - start_row) // 2, start_col)
        
        # Update castling rights
        # If king moves, that color loses all castling rights
        if moving_piece.type == PieceType.KING:
            if moving_piece.color == Color.WHITE:
                new_board.castling_rights = new_board.castling_rights.replace('K', '').replace('Q', '')
            else:
                new_board.castling_rights = new_board.castling_rights.replace('k', '').replace('q', '')
        
        # If a rook moves from its starting square, or is captured on its starting square, 
        # remove corresponding castling rights.
        # White Kingside rook (h1 -> (7,7))
        if ((start_row, start_col) == (7, 7) or (end_row, end_col) == (7, 7)) and moving_piece.color == Color.WHITE:
            new_board.castling_rights = new_board.castling_rights.replace('K', '')
        # White Queenside rook (a1 -> (7,0))
        if ((start_row, start_col) == (7, 0) or (end_row, end_col) == (7, 0)) and moving_piece.color == Color.WHITE:
            new_board.castling_rights = new_board.castling_rights.replace('Q', '')
        # Black Kingside rook (h8 -> (0,7))
        if ((start_row, start_col) == (0, 7) or (end_row, end_col) == (0, 7)) and moving_piece.color == Color.BLACK:
            new_board.castling_rights = new_board.castling_rights.replace('k', '')
        # Black Queenside rook (a8 -> (0,0))
        if ((start_row, start_col) == (0, 0) or (end_row, end_col) == (0, 0)) and moving_piece.color == Color.BLACK:
            new_board.castling_rights = new_board.castling_rights.replace('q', '')
        
        # Ensure castling_rights is not empty string, use '-' if no rights remain
        if not new_board.castling_rights:
            new_board.castling_rights = '-'

        # Update turn and fullmove number
        if new_board.turn == Color.BLACK:
            new_board.fullmove_number += 1
        new_board.turn = Color.WHITE if new_board.turn == Color.BLACK else Color.BLACK

        # Update FEN and history for threefold repetition
        new_board.current_fen = new_board.to_fen()
        new_board.history.append(new_board.current_fen)

        return new_board

    def get_game_status(self, board: Board) -> GameStatus:
        """Determines the current status of the game (e.g., ongoing, checkmate, stalemate, draw)."""
        current_player = board.turn
        
        # Check for Checkmate or Stalemate: iterate all pseudo-legal moves and check their legality
        legal_moves_exist = False
        for r_start in range(8):
            for c_start in range(8):
                piece = board.get_piece(r_start, c_start)
                if piece and piece.color == current_player:
                    # Iterate through all possible target squares (64 squares) for each piece
                    for r_end in range(8):
                        for c_end in range(8):
                            # Skip if starting and ending on the same square (already handled in is_move_legal, but defensive)
                            if r_start == r_end and c_start == c_end:
                                continue
                            
                            # For pawn promotion, try all valid promotion pieces if on the last rank
                            if piece.type == PieceType.PAWN and (r_end == 0 or r_end == 7):
                                for promo_type in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                                    temp_move = Move(r_start, c_start, r_end, c_end, promo_type)
                                    if self.is_move_legal(board, temp_move):
                                        legal_moves_exist = True
                                        break # Found a legal move, no need to check other promotion types
                                if legal_moves_exist: break # Found a legal move for this (pawn) piece
                            else:
                                # For all other pieces or non-promotion pawn moves
                                temp_move = Move(r_start, c_start, r_end, c_end)
                                if self.is_move_legal(board, temp_move):
                                    legal_moves_exist = True
                                    break # Found a legal move for this piece
                        if legal_moves_exist: break # Found a legal move for this starting square
                if legal_moves_exist: break # Found a legal move for the current player
        
        is_current_player_in_check = self._is_king_in_check(board, current_player)

        if not legal_moves_exist:
            if is_current_player_in_check:
                return GameStatus.CHECKMATE
            else:
                return GameStatus.STALEMATE

        # If there are legal moves, but the king is currently in check
        if is_current_player_in_check:
            return GameStatus.CHECK
        
        # Check for Draw conditions
        # 1. Fifty-move rule
        if board.halfmove_clock >= 100:
            return GameStatus.DRAW_FIFTY_MOVE

        # 2. Threefold repetition
        # For threefold repetition, only compare the first four FEN parts (position, active color, castling, en passant).
        fen_parts_for_repetition = board.to_fen().split(' ')[:4] # Get Pos, Turn, Castling, EnPassant
        current_position_signature = " ".join(fen_parts_for_repetition)
        
        repetition_count = 0
        # Iterate through history, but not the very last move (current board state) as it's not yet part of history for repetition count
        for historic_fen_full in board.history[:-1]: 
            historic_fen_parts = historic_fen_full.split(' ')[:4]
            historic_position_signature = " ".join(historic_fen_parts)
            if historic_position_signature == current_position_signature:
                repetition_count += 1
        
        if repetition_count >= 2: # >=2 means the position has occurred 3 times (initial + 2 repetitions)
            return GameStatus.DRAW_THREEFOLD_REPETITION

        # 3. Insufficient material
        pieces_on_board = []
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece:
                    pieces_on_board.append(piece)

        white_pieces = [p for p in pieces_on_board if p.color == Color.WHITE]
        black_pieces = [p for p in pieces_on_board if p.color == Color.BLACK]

        def get_material_signature(piece_list: List[Piece]) -> Tuple[int, int, int, int, int]:
            kings = sum(1 for p in piece_list if p.type == PieceType.KING)
            queens = sum(1 for p in piece_list if p.type == PieceType.QUEEN)
            rooks = sum(1 for p in piece_list if p.type == PieceType.ROOK)
            bishops = sum(1 for p in piece_list if p.type == PieceType.BISHOP)
            knights = sum(1 for p in piece_list if p.type == PieceType.KNIGHT)
            pawns = sum(1 for p in piece_list if p.type == PieceType.PAWN)
            return (kings, queens, rooks, bishops, knights, pawns)

        white_signature = get_material_signature(white_pieces)
        black_signature = get_material_signature(black_pieces)

        # Check basic insufficient material scenarios (King vs King, King+minor vs King)
        # K vs K
        if white_signature == (1, 0, 0, 0, 0, 0) and black_signature == (1, 0, 0, 0, 0, 0):
            return GameStatus.DRAW_INSUFFICIENT_MATERIAL
        # K+N vs K
        if (white_signature == (1, 0, 0, 0, 1, 0) and black_signature == (1, 0, 0, 0, 0, 0)) or \
           (white_signature == (1, 0, 0, 0, 0, 0) and black_signature == (1, 0, 0, 0, 1, 0)): 
            return GameStatus.DRAW_INSUFFICIENT_MATERIAL
        # K+B vs K
        if (white_signature == (1, 0, 0, 1, 0, 0) and black_signature == (1, 0, 0, 0, 0, 0)) or \
           (white_signature == (1, 0, 0, 0, 0, 0) and black_signature == (1, 0, 0, 1, 0, 0)): 
            return GameStatus.DRAW_INSUFFICIENT_MATERIAL
        
        # K+B vs K+B with bishops on the same color squares
        if white_signature == (1, 0, 0, 1, 0, 0) and black_signature == (1, 0, 0, 1, 0, 0):
            white_bishop_pos = None
            black_bishop_pos = None
            for r_idx in range(8):
                for c_idx in range(8):
                    p = board.get_piece(r_idx, c_idx)
                    if p and p.type == PieceType.BISHOP:
                        if p.color == Color.WHITE: white_bishop_pos = (r_idx, c_idx)
                        if p.color == Color.BLACK: black_bishop_pos = (r_idx, c_idx)
            
            if white_bishop_pos and black_bishop_pos:
                # Check if bishops are on the same color squares: (row+col) % 2 is same
                if (white_bishop_pos[0] + white_bishop_pos[1]) % 2 == (black_bishop_pos[0] + black_bishop_pos[1]) % 2:
                    return GameStatus.DRAW_INSUFFICIENT_MATERIAL

        # If none of the above conditions met, the game is still ongoing
        return GameStatus.ONGOING
