from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np


class Player(ABC):
    """Abstract base class for all players (AI and human)."""

    def __init__(self, name: str, player_id: int):
        """
        Initialize player.

        Args:
            name: Player's name.
            player_id: Player identifier (-1 or 1).
        """
        self.name = name
        self.player_id = player_id

    @abstractmethod
    def get_move(self, board: np.ndarray, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Get the player's move.

        Args:
            board: Current board state (numpy array with -1, 0, 1).
            valid_moves: List of valid moves as (row, col) tuples.

        Returns:
            (row, col) representing the chosen move.
        """

    def game_over(self, winner: int) -> None:
        """
        Optional hook called when the game is over.

        Args:
            winner: -1 or 1 if a player won, or 0 for a draw.
        """

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, player_id={self.player_id})"
