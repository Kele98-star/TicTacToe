import numpy as np
from typing import Tuple, Optional
from tictactoe.player_interface import Player


class MinimaxPlayer(Player):
    """
    AI player using minimax algorithm with alpha-beta pruning.
    Suitable for smaller boards (3x3 to ~5x5).
    For large boards, uses depth limit.
    """

    def __init__(self, name: str = "Minimax AI", player_id: int = -1, max_depth: int = None):
        """
        Initialize minimax player.

        Args:
            name: Player's name
            player_id: Player identifier (-1 or 1)
            max_depth: Maximum search depth (None for unlimited, recommended for large boards)
        """
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.board_size = None
        self.win_length = None

    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """
        Choose best move using minimax algorithm.

        Args:
            board: Current board state
            valid_moves: List of valid moves

        Returns:
            Best move as (row, col)
        """
        if not valid_moves:
            raise ValueError("No valid moves available")

        # Initialize board parameters
        self.board_size = board.shape[0]
        self.win_length = min(5, self.board_size)  # Assume standard win length

        # If no depth limit set, use heuristic based on board size
        if self.max_depth is None:
            if self.board_size <= 3:
                depth_limit = float('inf')
            elif self.board_size <= 5:
                depth_limit = 6
            else:
                depth_limit = 3
        else:
            depth_limit = self.max_depth

        best_score = -float('inf')
        best_move = valid_moves[0]

        for move in valid_moves:
            row, col = move
            # Make move
            board[row, col] = self.player_id

            # Evaluate position
            score = self._minimax(board, 0, False, -float('inf'), float('inf'), depth_limit)

            # Undo move
            board[row, col] = 0

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board: np.ndarray, depth: int, is_maximizing: bool,
                 alpha: float, beta: float, max_depth: int) -> float:
        """
        Minimax algorithm with alpha-beta pruning.

        Args:
            board: Current board state
            depth: Current search depth
            is_maximizing: Whether this is a maximizing node
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            max_depth: Maximum search depth

        Returns:
            Score of the position
        """
        # Check terminal conditions
        winner = self._check_winner(board)
        if winner is not None:
            if winner == self.player_id:
                return 1000 - depth  # Prefer faster wins
            elif winner == -self.player_id:
                return -1000 + depth  # Prefer slower losses
            else:
                return 0  # Draw

        # Check depth limit
        if depth >= max_depth:
            return self._evaluate_position(board)

        valid_moves = list(zip(*np.where(board == 0)))
        if not valid_moves:
            return 0  # Draw

        if is_maximizing:
            max_eval = -float('inf')
            for row, col in valid_moves:
                board[row, col] = self.player_id
                eval = self._minimax(board, depth + 1, False, alpha, beta, max_depth)
                board[row, col] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for row, col in valid_moves:
                board[row, col] = -self.player_id
                eval = self._minimax(board, depth + 1, True, alpha, beta, max_depth)
                board[row, col] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _check_winner(self, board: np.ndarray) -> Optional[int]:
        """
        Check if there's a winner on the board.

        Returns:
            Player ID if there's a winner, 0 for draw, None if game continues
        """
        # Check rows, columns, and diagonals for wins
        for player in [-1, 1]:
            if self._has_won(board, player):
                return player

        # Check for draw
        if not np.any(board == 0):
            return 0

        return None

    def _has_won(self, board: np.ndarray, player: int) -> bool:
        """Check if a player has won."""
        # For efficiency on large boards, only check recent high-value positions
        # This is a simplified check - full check would be more expensive

        # Check rows
        for i in range(self.board_size):
            for j in range(self.board_size - self.win_length + 1):
                if np.all(board[i, j:j + self.win_length] == player):
                    return True

        # Check columns
        for i in range(self.board_size - self.win_length + 1):
            for j in range(self.board_size):
                if np.all(board[i:i + self.win_length, j] == player):
                    return True

        # Check diagonals (main direction)
        for i in range(self.board_size - self.win_length + 1):
            for j in range(self.board_size - self.win_length + 1):
                if all(board[i + k, j + k] == player for k in range(self.win_length)):
                    return True

        # Check diagonals (anti direction)
        for i in range(self.board_size - self.win_length + 1):
            for j in range(self.win_length - 1, self.board_size):
                if all(board[i + k, j - k] == player for k in range(self.win_length)):
                    return True

        return False

    def _evaluate_position(self, board: np.ndarray) -> float:
        """
        Evaluate the board position heuristically.

        Returns:
            Score from perspective of self.player_id
        """
        score = 0

        # Count threats and opportunities
        for player in [self.player_id, -self.player_id]:
            multiplier = 1 if player == self.player_id else -1

            # Evaluate rows
            for i in range(self.board_size):
                for j in range(self.board_size - self.win_length + 1):
                    window = board[i, j:j + self.win_length]
                    score += multiplier * self._evaluate_window(window, player)

            # Evaluate columns
            for i in range(self.board_size - self.win_length + 1):
                for j in range(self.board_size):
                    window = board[i:i + self.win_length, j]
                    score += multiplier * self._evaluate_window(window, player)

        return score

    def _evaluate_window(self, window: np.ndarray, player: int) -> float:
        """Evaluate a window of cells."""
        player_count = np.sum(window == player)
        empty_count = np.sum(window == 0)
        opponent_count = np.sum(window == -player)

        # If opponent has pieces, this window is blocked
        if opponent_count > 0:
            return 0

        # Score based on how many pieces we have
        if player_count == self.win_length - 1 and empty_count == 1:
            return 10  # One move from winning
        elif player_count == self.win_length - 2 and empty_count == 2:
            return 5  # Two moves from winning
        elif player_count > 0:
            return player_count

        return 0
