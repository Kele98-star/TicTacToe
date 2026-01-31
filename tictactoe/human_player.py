import numpy as np
from typing import Tuple
from tictactoe.player_interface import Player


class HumanPlayer(Player):
    """
    Human player that takes input from the terminal.
    """

    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """
        Get move from human input.

        Args:
            board: Current board state
            valid_moves: List of valid moves

        Returns:
            Tuple of (row, col)
        """
        while True:
            try:
                move_input = input(f"{self.name}, enter your move (row col): ").strip()
                parts = move_input.split()

                if len(parts) != 2:
                    print("Please enter row and column separated by space (e.g., '0 0')")
                    continue

                row, col = int(parts[0]), int(parts[1])

                if (row, col) in valid_moves:
                    return row, col
                else:
                    print(f"Invalid move. Please choose from valid moves.")
                    print(f"Valid moves: {valid_moves[:10]}{'...' if len(valid_moves) > 10 else ''}")

            except ValueError:
                print("Please enter valid integers for row and column.")
            except KeyboardInterrupt:
                print("\nGame interrupted by user.")
                raise
            except Exception as e:
                print(f"Error: {e}")
