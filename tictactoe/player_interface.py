from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple


class Player(ABC):
    """
    Abstract base class for all players (AI and human).
    """

    def __init__(self, name: str, player_id: int):
        """
        Initialize player.

        Args:
            name: Player's name
            player_id: Player identifier (-1 or 1)
        """
        self.name = name
        self.player_id = player_id

    @abstractmethod
    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """
        Get the player's move.

        Args:
            board: Current board state (numpy array with -1, 0, 1)
            valid_moves: List of valid moves as (row, col) tuples

        Returns:
            Tuple of (row, col) representing the chosen move
        """
        pass

    def game_over(self, winner: int):
        """
        Called when the game is over.

        Args:
            winner: -1, 1 (player won), or 0 (draw)
        """
        pass

    def __str__(self):
        return self.name
