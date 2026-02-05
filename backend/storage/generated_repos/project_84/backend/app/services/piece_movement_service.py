from dataclasses import dataclass
from typing import List, Tuple, Optional

# --- Models (Stubs for demonstration within this file) ---
# In a real application, these would typically be imported from a dedicated app.models module
@dataclass
class Piece:
    id: str
    type: str # e.g., "pawn", "rook", "knight", "bishop", "queen", "king"
    color: str # "white", "black"
    position: Tuple[int, int] # (row, col) e.g., (0,0) to (7,7)
    has_moved: bool = False # Useful for pawns (initial 2-step) and kings/rooks (castling)

@dataclass
class Move:
    piece_id: str
    start_pos: Tuple[int, int]
    end_pos: Tuple[int, int]
    is_capture: bool = False
    captured_piece_id: Optional[str] = None
    # Additional fields could be added for promotion, castling, en passant, etc.

@dataclass
class Board:
    width: int
    height: int
    pieces: List[Piece] # All pieces currently on the board

    def get_piece_at(self, x: int, y: int) -> Optional[Piece]:
        """Retrieves the piece at a given board position, if any."""
        for p in self.pieces:
            if p.position == (x, y):
                return p
        return None

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Checks if the given coordinates are within the board's bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_piece_color_at(self, x: int, y: int) -> Optional[str]:
        """Returns the color of the piece at (x,y), or None if empty."""
        piece = self.get_piece_at(x, y)
        return piece.color if piece else None
# --- End Models ---


class PieceMovementService:
    """
    Service responsible for implementing and validating custom piece movement rules for chess variants.
    It calculates all legal moves for a given piece and checks for path obstructions.
    """

    def _is_valid_move_target(self, board: Board, target_pos: Tuple[int, int], piece_color: str) -> Tuple[bool, bool, Optional[Piece]]:
        """
        Checks if a target position is valid for a move/capture considering board bounds and piece occupancy.
        Returns (is_valid_target, is_capture, captured_piece).
        """
        if not board.is_within_bounds(target_pos[0], target_pos[1]):
            return False, False, None

        target_piece = board.get_piece_at(target_pos[0], target_pos[1])
        if target_piece:
            if target_piece.color == piece_color:
                # Cannot move to a square occupied by an own piece
                return False, False, None
            else:
                # Can capture an opponent's piece
                return True, True, target_piece
        else:
            # Empty square, can move there
            return True, False, None

    def is_path_clear(self, board: Board, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        """
        Checks if the path between two positions is clear of pieces.
        Assumes start_pos and end_pos are on a straight line (horizontal, vertical, or diagonal).
        Does not check start_pos or end_pos, only intermediate squares.
        Returns True if the path is clear, False otherwise or if the path is not a straight line.
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Check if the path is straight (horizontal, vertical, or diagonal) for the purpose of this check
        dr = abs(end_row - start_row)
        dc = abs(end_col - start_col)
        if not ((dr == 0 and dc > 0) or (dc == 0 and dr > 0) or (dr == dc and dr > 0)):
            # If start_pos == end_pos, the path is trivially clear (no intermediate squares).
            if start_pos == end_pos: return True
            # Not a straight line or no movement, so path clearance is not applicable in this context
            return False

        # Determine direction steps
        step_row = 0
        if end_row > start_row: step_row = 1
        elif end_row < start_row: step_row = -1

        step_col = 0
        if end_col > start_col: step_col = 1
        elif end_col < start_col: step_col = -1

        # Iterate through intermediate squares
        current_row, current_col = start_row + step_row, start_col + step_col

        while (current_row, current_col) != end_pos:
            if not board.is_within_bounds(current_row, current_col):
                # Should not happen if start/end positions are within bounds and logic is correct.
                return False
            if board.get_piece_at(current_row, current_col):
                return False # Path is blocked by a piece
            current_row += step_row
            current_col += step_col
        return True # Path is clear

    def calculate_legal_moves(self, piece: Piece, board: Board) -> List[Move]:
        """
        Calculates all legal moves for a given piece based on standard chess rules and board state.
        This method can be extended to support custom piece movement rules for chess variants.
        """
        legal_moves: List[Move] = []
        start_row, start_col = piece.position
        piece_color = piece.color
        opponent_color = "black" if piece_color == "white" else "white"

        # Helper function to try adding a move to the list
        def _try_add_move(target_row: int, target_col: int) -> Tuple[bool, bool]:
            target_pos = (target_row, target_col)
            is_valid_target, is_capture, captured_piece = self._is_valid_move_target(board, target_pos, piece_color)

            if is_valid_target:
                legal_moves.append(Move(
                    piece_id=piece.id,
                    start_pos=piece.position,
                    end_pos=target_pos,
                    is_capture=is_capture,
                    captured_piece_id=captured_piece.id if captured_piece else None
                ))
            return is_valid_target, is_capture # Return status for conditional logic in sliding pieces

        # --- Piece-specific movement logic ---
        if piece.type == "pawn":
            direction = 1 if piece_color == "white" else -1
            
            # Forward one square
            target_row_one_step = start_row + direction
            if board.is_within_bounds(target_row_one_step, start_col) and not board.get_piece_at(target_row_one_step, start_col):
                _try_add_move(target_row_one_step, start_col)

                # Forward two squares (only on first move, if one square forward is also clear)
                if not piece.has_moved:
                    target_row_two_steps = start_row + 2 * direction
                    if board.is_within_bounds(target_row_two_steps, start_col) and \
                       not board.get_piece_at(target_row_two_steps, start_col) and \
                       not board.get_piece_at(target_row_one_step, start_col): # Ensure intermediate square is clear
                        _try_add_move(target_row_two_steps, start_col)

            # Captures (diagonal)
            for col_offset in [-1, 1]:
                target_row_capture = start_row + direction
                target_col_capture = start_col + col_offset
                if board.is_within_bounds(target_row_capture, target_col_capture):
                    target_piece = board.get_piece_at(target_row_capture, target_col_capture)
                    if target_piece and target_piece.color == opponent_color:
                        _try_add_move(target_row_capture, target_col_capture)

            # TODO: Implement En passant and Pawn Promotion rules

        elif piece.type == "knight":
            knight_offsets = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]
            for dr, dc in knight_offsets:
                _try_add_move(start_row + dr, start_col + dc)

        elif piece.type == "king":
            king_offsets = [
                (0, 1), (0, -1), (1, 0), (-1, 0),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
            for dr, dc in king_offsets:
                _try_add_move(start_row + dr, start_col + dc)
            # TODO: Implement Castling rules and check for moving into check

        elif piece.type in ["rook", "bishop", "queen"]:
            directions = []
            if piece.type == "rook" or piece.type == "queen":
                # Horizontal and Vertical movements
                directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
            if piece.type == "bishop" or piece.type == "queen":
                # Diagonal movements
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])

            for dr, dc in directions:
                current_row, current_col = start_row, start_col
                while True:
                    current_row += dr
                    current_col += dc
                    
                    # Attempt to add the move; checks bounds and piece conflict
                    is_valid, is_capture = _try_add_move(current_row, current_col)

                    if not is_valid: # Either out of bounds or blocked by own piece
                        break # Stop moving in this direction
                    if is_capture: # Captured an opponent's piece, cannot move past it
                        break
                    # If is_valid and not is_capture, it's an empty square, continue in this direction.
        
        return legal_moves