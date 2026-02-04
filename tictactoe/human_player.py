from typing import Tuple
from tictactoe.player_interface import Player


class HumanPlayer(Player):
    """Terminal-based human player."""

    def get_move(self, board, valid_moves: list) -> Tuple[int, int]:
        """
        Prompt the user for a move until a valid (row, col) is provided.
        """
        valid_move_set = set(valid_moves)
        max_preview = 10

        while True:
            try:
                move_input = input(f"{self.name}, enter your move as 'row col': ").strip()
                row_str, col_str = move_input.split()
                row, col = int(row_str), int(col_str)
            except ValueError:
                print("Please enter two integers separated by a space, e.g. '0 0'.")
                continue
            except KeyboardInterrupt:
                print("\nGame interrupted by user.")
                raise

            move = (row, col)
            if move in valid_move_set:
                return move

            print("Invalid move. Please choose one of the valid moves.")
            if valid_moves:
                preview = ", ".join(f"({r}, {c})" for r, c in valid_moves[:max_preview])
                suffix = "..." if len(valid_moves) > max_preview else ""
                print(f"Valid moves: {preview}{suffix}")
