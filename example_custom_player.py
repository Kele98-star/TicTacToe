"""
Example custom player implementation.

This file shows how to create your own AI player for the tic-tac-toe game.
Your custom player should:
1. Inherit from the Player class
2. Implement the get_move() method
3. Optionally override the game_over() method

To use this player:
python -m tictactoe.main --player1 example_custom_player.py --player2 random --games 10
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import tictactoe
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from typing import Tuple
from tictactoe.player_interface import Player


class CenterPreferringPlayer(Player):
    """
    Example AI that prefers to play near the center of the board.
    Falls back to random moves if center area is full.
    """

    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """
        Choose a move, preferring positions near the center.

        Args:
            board: Current board state (numpy array with -1, 0, 1)
            valid_moves: List of valid moves as (row, col) tuples

        Returns:
            Chosen move as (row, col)
        """
        if not valid_moves:
            raise ValueError("No valid moves available")

        board_size = board.shape[0]
        center = board_size // 2

        # Score each move based on distance to center
        best_move = None
        best_score = float('inf')

        for row, col in valid_moves:
            # Calculate Manhattan distance to center
            distance = abs(row - center) + abs(col - center)

            # Add some randomness to avoid always picking the same pattern
            score = distance + np.random.random() * 0.5

            if score < best_score:
                best_score = score
                best_move = (row, col)

        return best_move

    def game_over(self, winner: int):
        """
        Called when the game ends.
        You can use this to track statistics, learn from games, etc.
        """
        # Optional: track wins/losses
        pass


class CornerPreferringPlayer(Player):
    """
    Another example AI that prefers corners, then edges, then center.
    """

    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """Choose a move, preferring corners."""
        if not valid_moves:
            raise ValueError("No valid moves available")

        board_size = board.shape[0]
        max_idx = board_size - 1

        # Check for corners
        corners = [(0, 0), (0, max_idx), (max_idx, 0), (max_idx, max_idx)]
        for corner in corners:
            if corner in valid_moves:
                return corner

        # Check for edges (not corners)
        edges = []
        for i in range(board_size):
            edges.append((0, i))
            edges.append((max_idx, i))
            edges.append((i, 0))
            edges.append((i, max_idx))

        for edge in edges:
            if edge in valid_moves and edge not in corners:
                return edge

        # Fall back to first available move
        return valid_moves[0]


# You can have multiple player classes in one file.
# The game will use the first Player subclass it finds.
# To use a specific one, you can make it the only one, or put it first.
