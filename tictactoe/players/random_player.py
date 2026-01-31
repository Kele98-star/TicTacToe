import numpy as np
import random
from typing import Tuple
from tictactoe.player_interface import Player


class RandomPlayer(Player):
    """
    AI player that makes random valid moves.
    """

    def __init__(self, name: str = "Random AI", player_id: int = -1, seed: int = None):
        """
        Initialize random player.

        Args:
            name: Player's name
            player_id: Player identifier (-1 or 1)
            seed: Random seed for reproducibility
        """
        super().__init__(name, player_id)
        if seed is not None:
            random.seed(seed)

    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """
        Choose a random valid move.

        Args:
            board: Current board state
            valid_moves: List of valid moves

        Returns:
            Random valid move as (row, col)
        """
        return random.choice(valid_moves)
