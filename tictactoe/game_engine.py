import numpy as np
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

class TicTacToeGame:
    """
    Core game engine for tic-tac-toe.
    Uses -1, 0, 1 to represent players and empty cells.
    -1: Player 1
     0: Empty
     1: Player 2
    """
    def __init__(self, size: int = 100, win_length: int = None):
        """
        Initialize the game.
        Args:
            size: Board size (size x size)
            win_length: Number in a row needed to win (defaults to size for small boards, 5 for large boards)
        """
        self.size = size
        self.win_length = win_length or (size if size <= 5 else 5)
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = -1  # Player 1 starts
        self.move_history = []
        self.game_over = False
        self.winner = None
        self.empty_count = size * size

    def reset(self):
        """Reset the game to initial state."""
        self.board.fill(0)
        self.current_player = -1
        self.move_history = []
        self.game_over = False
        self.winner = None
        self.empty_count = self.size * self.size

    def get_valid_moves(self) -> list:
        """Return list of valid moves as (row, col) tuples."""
        return list(zip(*np.where(self.board == 0)))

    def make_move(self, row: int, col: int) -> bool:
        """
        Make a move on the board.
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
        Returns:
            True if move was valid and made, False otherwise
        """
        if self.game_over:
            return False
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.board[row, col] != 0:
            return False

        self.board[row, col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        self.empty_count -= 1

        if self._check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        elif self.empty_count == 0:
            self.game_over = True
            self.winner = 0  # Draw
        else:
            self.current_player = -self.current_player
        return True

    def _check_win(self, row: int, col: int) -> bool:
        """Check if the last move at (row, col) resulted in a win."""
        player = self.board[row, col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            if self._check_line(row, col, dr, dc, player):
                return True
        return False

    def _check_line(self, row: int, col: int, dr: int, dc: int, player: int) -> bool:
        """
        Check if there's a winning line through (row, col) in direction (dr, dc).
        """
        count = 1
        # Positive direction
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r, c] == player:
            count += 1
            r += dr
            c += dc
        # Negative direction
        r, c = row - dr, col - dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r, c] == player:
            count += 1
            r -= dr
            c -= dc
        return count >= self.win_length

    def get_board_copy(self) -> np.ndarray:
        """Return a copy of the current board state."""
        return self.board.copy()

    def display(self, clear_screen: bool = True):
        """Display the board in the terminal."""
        if clear_screen:
            clear()

        symbols = {-1: 'X', 0: '.', 1: 'O'}
        latest_move = self.move_history[-1][:2] if self.move_history else None

        # Print column numbers
        label_width = 2 if self.size <= 26 else 3
        print(" " * (label_width + 1), end="")
        for col in range(self.size):
            if self.size <= 26:
                print(f"{col:2}", end=" ")
            else:
                print(f"{col:3}", end=" ")
        print()

        # Print board
        for row in range(self.size):
            if self.size <= 26:
                print(f"{row:2} ", end="")
            else:
                print(f"{row:3} ", end="")
            for col in range(self.size):
                symbol = symbols[self.board[row, col]]
                if latest_move and (row, col) == latest_move:
                    print(f" \033[91m{symbol}\033[0m ", end="")
                else:
                    print(f" {symbol} ", end="")
            print()
        print()

    def get_state_info(self) -> dict:
        """Return current game state information."""
        return {
            'board': self.get_board_copy(),
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_count': len(self.move_history)
        }
