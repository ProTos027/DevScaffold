from typing import List, Tuple, Optional, Dict
from pydantic import BaseModel

# --- MOCK MODELS --- (In a real application, these would be imported from app.models)
# Assuming a simple board representation where 0,0 is a8 and 7,7 is h1
# Alg notation: 'a1' -> (7,0), 'h8' -> (0,7)

class Piece(BaseModel):
    id: str
    type: str # e.g., 'Pawn', 'Knight', 'Bishop', 'Rook', 'Queen', 'King'
    color: str # 'white' or 'black'
    pos: Tuple[int, int] # (row, col)

    def dict(self, *args, **kwargs):
        # Custom dict method to include 'pos' as a list for JSON serialization if needed
        return {
            "id": self.id,
            "type": self.type,
            "color": self.color,
            "pos": list(self.pos)
        }

class BoardState(BaseModel):
    game_id: str
    board: List[List[Optional[Piece]]] # 8x8 grid
    current_turn_color: str # 'white' or 'black'
    white_king_pos: Tuple[int, int]
    black_king_pos: Tuple[int, int]
    # Add other state like castling rights, en passant target, half-move clock, etc.
    # For this implementation, we simplify and omit advanced state fields.

# --- END MOCK MODELS ---

class GameLogicService:
    def __init__(self):
        # In a real application, this would interact with a database or cache
        self._game_states: Dict[str, BoardState] = {}

    def _get_board_state(self, game_id: str) -> Optional[BoardState]:
        # Mock data retrieval
        return self._game_states.get(game_id)

    def _update_board_state(self, board_state: BoardState):
        # Mock data storage
        self._game_states[board_state.game_id] = board_state

    def _alg_to_coords(self, alg_pos: str) -> Tuple[int, int]:
        """Converts algebraic notation (e.g., 'a1') to (row, col) coordinates."""
        file_char = alg_pos[0]
        rank_char = alg_pos[1]
        col = ord(file_char) - ord('a')
        row = 8 - int(rank_char)
        return row, col

    def _coords_to_alg(self, row: int, col: int) -> str:
        """Converts (row, col) coordinates to algebraic notation."""
        file_char = chr(ord('a') + col)
        rank_char = str(8 - row)
        return f"{file_char}{rank_char}"

    def _is_valid_coords(self, r: int, c: int) -> bool:
        """Checks if coordinates are within the board boundaries."""
        return 0 <= r < 8 and 0 <= c < 8

    def _get_piece_at(self, board: List[List[Optional[Piece]]], r: int, c: int) -> Optional[Piece]:
        if self._is_valid_coords(r, c):
            return board[r][c]
        return None

    def _is_king_in_check(self, board: List[List[Optional[Piece]]], king_color: str, king_pos: Tuple[int, int]) -> bool:
        king_r, king_c = king_pos
        opponent_color = 'white' if king_color == 'black' else 'black'

        # Directions for each piece type to check for attacks
        directions = {
            'Pawn': {
                'white': [(-1, -1), (-1, 1)], # Diagonal captures
                'black': [(1, -1), (1, 1)]
            },
            'Knight': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
            'Bishop': [(-1, -1), (-1, 1), (1, -1), (1, 1)], # Diagonals
            'Rook': [(-1, 0), (1, 0), (0, -1), (0, 1)], # Straights
            'Queen': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)], # All
            'King': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)] # All 1 step
        }

        # Check for attacks from various pieces
        for dr, dc in directions['Queen']:
            for i in range(1, 8):
                r, c = king_r + dr * i, king_c + dc * i
                if not self._is_valid_coords(r, c):
                    break
                piece = self._get_piece_at(board, r, c)
                if piece:
                    if piece.color == opponent_color:
                        if piece.type == 'Queen': return True
                        if dr == 0 or dc == 0: # Straight line
                            if piece.type == 'Rook': return True
                        else: # Diagonal line
                            if piece.type == 'Bishop': return True
                    break # Piece blocking line of sight

        # Check for Knight attacks
        for dr, dc in directions['Knight']:
            r, c = king_r + dr, king_c + dc
            piece = self._get_piece_at(board, r, c)
            if piece and piece.color == opponent_color and piece.type == 'Knight':
                return True

        # Check for Pawn attacks
        pawn_attacks = directions['Pawn'][king_color]
        for dr, dc in pawn_attacks:
            r, c = king_r + dr, king_c + dc
            piece = self._get_piece_at(board, r, c)
            if piece and piece.color == opponent_color and piece.type == 'Pawn':
                return True

        # Check for King attacks (adjacent opponent king, for validation during move generation)
        for dr, dc in directions['King']:
            r, c = king_r + dr, king_c + dc
            piece = self._get_piece_at(board, r, c)
            if piece and piece.color == opponent_color and piece.type == 'King':
                return True

        return False

    def _get_pseudo_legal_moves(self, board: List[List[Optional[Piece]]], piece: Piece) -> List[Tuple[int, int]]:
        """Calculates all moves for a piece, ignoring whether the move leaves the king in check."""
        moves = []
        r, c = piece.pos
        color = piece.color
        opponent_color = 'white' if color == 'black' else 'black'

        def _add_straight_moves(dr: int, dc: int):
            for i in range(1, 8):
                new_r, new_c = r + dr * i, c + dc * i
                if not self._is_valid_coords(new_r, new_c): break
                target_piece = self._get_piece_at(board, new_r, new_c)
                if target_piece:
                    if target_piece.color == opponent_color: moves.append((new_r, new_c))
                    break # Stop if a piece is encountered
                moves.append((new_r, new_c))

        def _add_knight_moves():
            knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_offsets:
                new_r, new_c = r + dr, c + dc
                if self._is_valid_coords(new_r, new_c):
                    target_piece = self._get_piece_at(board, new_r, new_c)
                    if not target_piece or target_piece.color == opponent_color: moves.append((new_r, new_c))

        def _add_king_moves():
            king_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in king_offsets:
                new_r, new_c = r + dr, c + dc
                if self._is_valid_coords(new_r, new_c):
                    target_piece = self._get_piece_at(board, new_r, new_c)
                    if not target_piece or target_piece.color == opponent_color: moves.append((new_r, new_c))
            # TODO: Implement castling logic

        def _add_pawn_moves():
            direction = -1 if color == 'white' else 1
            start_rank = 6 if color == 'white' else 1

            # One step forward
            new_r, new_c = r + direction, c
            if self._is_valid_coords(new_r, new_c) and not self._get_piece_at(board, new_r, new_c):
                moves.append((new_r, new_c))

                # Two steps forward (from starting rank)
                if r == start_rank:
                    new_r2, new_c2 = r + 2 * direction, c
                    if not self._get_piece_at(board, new_r2, new_c2):
                        moves.append((new_r2, new_c2))

            # Captures
            for dc_capture in [-1, 1]:
                new_r_capture, new_c_capture = r + direction, c + dc_capture
                if self._is_valid_coords(new_r_capture, new_c_capture):
                    target_piece = self._get_piece_at(board, new_r_capture, new_c_capture)
                    if target_piece and target_piece.color == opponent_color:
                        moves.append((new_r_capture, new_c_capture))
            # TODO: Implement en passant logic
            # TODO: Implement pawn promotion logic (for actual move application)

        if piece.type == 'Pawn': _add_pawn_moves()
        elif piece.type == 'Knight': _add_knight_moves()
        elif piece.type == 'Bishop': # Diagonal moves
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]: _add_straight_moves(dr, dc)
        elif piece.type == 'Rook': # Straight moves
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: _add_straight_moves(dr, dc)
        elif piece.type == 'Queen': # All straight and diagonal moves
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]: _add_straight_moves(dr, dc)
        elif piece.type == 'King': _add_king_moves()
        # Add custom piece movement rules here if any

        return moves

    def _get_all_legal_moves_for_color(self, board_state: BoardState, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        all_legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = self._get_piece_at(board_state.board, r, c)
                if piece and piece.color == color:
                    legal_moves_for_piece = self.get_legal_moves(board_state.game_id, self._coords_to_alg(r, c))
                    for move in legal_moves_for_piece:
                        all_legal_moves.append(((r, c), self._alg_to_coords(move)))
        return all_legal_moves

    def _simulate_move(self, original_board: List[List[Optional[Piece]]], piece_to_move: Piece, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> Tuple[List[List[Optional[Piece]]], Tuple[int, int]]:
        simulated_board = [row[:] for row in original_board] # Deep copy of the board
        simulated_piece = piece_to_move.copy(update={'pos': end_pos}) # Update piece's position

        # Perform the move
        simulated_board[start_pos[0]][start_pos[1]] = None
        simulated_board[end_pos[0]][end_pos[1]] = simulated_piece

        # Update king position if the king moved
        king_pos = None
        if piece_to_move.type == 'King':
            king_pos = end_pos
        else: # King didn't move, find its position on the simulated board
            original_king_pos = self._game_states[piece_to_move.game_id].white_king_pos if piece_to_move.color == 'white' else self._game_states[piece_to_move.game_id].black_king_pos
            king_pos = original_king_pos # This will be updated if it was the king moving.
            if original_king_pos == start_pos and piece_to_move.type != 'King': # if the piece moved was not the king but occupied the king's initial position, this is wrong.
                # This means we need to find the king on the board if the piece_to_move wasn't the king
                # A more robust solution would be to pass king positions explicitly or iterate to find it
                # For now, assuming king_pos is tracked separately
                pass # The external king_pos tracking will handle this based on piece_to_move.type

        return simulated_board, king_pos # king_pos might need better handling if not the king moved


    def validate_move(self, game_id: str, player_id: str, start_pos_alg: str, end_pos_alg: str) -> Dict[str, bool | str]:
        board_state = self._get_board_state(game_id)
        if not board_state: return {"is_valid": False, "message": "Game not found."}

        start_r, start_c = self._alg_to_coords(start_pos_alg)
        end_r, end_c = self._alg_to_coords(end_pos_alg)

        if not self._is_valid_coords(start_r, start_c) or not self._is_valid_coords(end_r, end_c):
            return {"is_valid": False, "message": "Invalid board coordinates."}

        piece = self._get_piece_at(board_state.board, start_r, start_c)
        if not piece: return {"is_valid": False, "message": "No piece at start position."}

        # Assuming player_id maps directly to color or we fetch player color from game_id and player_id
        # For simplicity, player_id is assumed to be the color 'white' or 'black'
        if piece.color != player_id: # player_id should be 'white' or 'black'
            return {"is_valid": False, "message": f"Piece belongs to opponent. It's {piece.color}'s turn."}

        if piece.color != board_state.current_turn_color:
            return {"is_valid": False, "message": f"It's not {piece.color}'s turn."}

        legal_moves_alg = self.get_legal_moves(game_id, start_pos_alg)
        if end_pos_alg not in legal_moves_alg:
            return {"is_valid": False, "message": "Move is not legal."}

        return {"is_valid": True, "message": "Move is legal."}

    def apply_move(self, game_id: str, player_id: str, start_pos_alg: str, end_pos_alg: str) -> Dict[str, bool | str]:
        validation_result = self.validate_move(game_id, player_id, start_pos_alg, end_pos_alg)
        if not validation_result["is_valid"]:
            return validation_result

        board_state = self._get_board_state(game_id)
        if not board_state: return {"success": False, "message": "Game not found."}

        start_r, start_c = self._alg_to_coords(start_pos_alg)
        end_r, end_c = self._alg_to_coords(end_pos_alg)

        piece_to_move = self._get_piece_at(board_state.board, start_r, start_c)
        if not piece_to_move: return {"success": False, "message": "No piece found, despite validation success. Internal error."}

        # Update piece position within the Piece object itself
        piece_to_move.pos = (end_r, end_c)

        # Perform the move on the board
        board_state.board[end_r][end_c] = piece_to_move # Capture or move
        board_state.board[start_r][start_c] = None

        # Update king's position if the king moved
        if piece_to_move.type == 'King':
            if piece_to_move.color == 'white':
                board_state.white_king_pos = (end_r, end_c)
            else:
                board_state.black_king_pos = (end_r, end_c)

        # Switch turn
        board_state.current_turn_color = 'white' if board_state.current_turn_color == 'black' else 'black'

        self._update_board_state(board_state)

        return {"success": True, "message": "Move applied successfully."}

    def get_legal_moves(self, game_id: str, piece_pos_alg: str) -> List[str]:
        board_state = self._get_board_state(game_id)
        if not board_state: return []

        r, c = self._alg_to_coords(piece_pos_alg)
        piece = self._get_piece_at(board_state.board, r, c)

        if not piece: return []

        pseudo_legal_moves = self._get_pseudo_legal_moves(board_state.board, piece)
        legal_moves = []

        # Iterate through pseudo-legal moves and check for king safety
        for end_r, end_c in pseudo_legal_moves:
            # Simulate the move on a temporary board
            simulated_board = [row[:] for row in board_state.board]
            simulated_piece = piece.copy(update={'pos': (end_r, end_c)})

            simulated_board[r][c] = None
            simulated_board[end_r][end_c] = simulated_piece

            # Determine the king's current position for the color that is moving
            king_color = piece.color
            current_king_pos = board_state.white_king_pos if king_color == 'white' else board_state.black_king_pos
            # If the moving piece is the king, update its position for the simulation check
            if piece.type == 'King':
                simulated_king_pos = (end_r, end_c)
            else:
                simulated_king_pos = current_king_pos

            if not self._is_king_in_check(simulated_board, king_color, simulated_king_pos):
                legal_moves.append(self._coords_to_alg(end_r, end_c))

        return legal_moves

    def check_game_status(self, game_id: str) -> Dict[str, str | None]:
        board_state = self._get_board_state(game_id)
        if not board_state: return {"status": "Game not found", "winner": None}

        current_player_color = board_state.current_turn_color
        king_pos = board_state.white_king_pos if current_player_color == 'white' else board_state.black_king_pos

        # Check if the current player's king is in check
        is_in_check = self._is_king_in_check(board_state.board, current_player_color, king_pos)

        # Find all legal moves for the current player
        all_legal_moves = self._get_all_legal_moves_for_color(board_state, current_player_color)

        if not all_legal_moves:
            if is_in_check:
                winner_color = 'white' if current_player_color == 'black' else 'black'
                return {"status": "Checkmate", "winner": winner_color}
            else:
                return {"status": "Stalemate", "winner": None}

        # TODO: Implement draw conditions (e.g., insufficient material, 50-move rule, threefold repetition)

        return {"status": "Ongoing", "winner": None}

    # --- Helper for initial board setup (for testing/demonstration) ---
    def initialize_new_game(self, game_id: str):
        initial_board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]

        # Pawns
        for c in range(8):
            initial_board[6][c] = Piece(id=f'wp{c}', type='Pawn', color='white', pos=(6, c))
            initial_board[1][c] = Piece(id=f'bp{c}', type='Pawn', color='black', pos=(1, c))

        # Rooks
        initial_board[7][0] = Piece(id='wr1', type='Rook', color='white', pos=(7, 0))
        initial_board[7][7] = Piece(id='wr2', type='Rook', color='white', pos=(7, 7))
        initial_board[0][0] = Piece(id='br1', type='Rook', color='black', pos=(0, 0))
        initial_board[0][7] = Piece(id='br2', type='Rook', color='black', pos=(0, 7))

        # Knights
        initial_board[7][1] = Piece(id='wn1', type='Knight', color='white', pos=(7, 1))
        initial_board[7][6] = Piece(id='wn2', type='Knight', color='white', pos=(7, 6))
        initial_board[0][1] = Piece(id='bn1', type='Knight', color='black', pos=(0, 1))
        initial_board[0][6] = Piece(id='bn2', type='Knight', color='black', pos=(0, 6))

        # Bishops
        initial_board[7][2] = Piece(id='wb1', type='Bishop', color='white', pos=(7, 2))
        initial_board[7][5] = Piece(id='wb2', type='Bishop', color='white', pos=(7, 5))
        initial_board[0][2] = Piece(id='bb1', type='Bishop', color='black', pos=(0, 2))
        initial_board[0][5] = Piece(id='bb2', type='Bishop', color='black', pos=(0, 5))

        # Queens
        initial_board[7][3] = Piece(id='wq', type='Queen', color='white', pos=(7, 3))
        initial_board[0][3] = Piece(id='bq', type='Queen', color='black', pos=(0, 3))

        # Kings
        initial_board[7][4] = Piece(id='wk', type='King', color='white', pos=(7, 4))
        initial_board[0][4] = Piece(id='bk', type='King', color='black', pos=(0, 4))

        new_board_state = BoardState(
            game_id=game_id,
            board=initial_board,
            current_turn_color='white',
            white_king_pos=(7, 4),
            black_king_pos=(0, 4)
        )
        self._update_board_state(new_board_state)
        return new_board_state
