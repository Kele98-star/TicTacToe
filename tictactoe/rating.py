"""ELO Rating System for TicTacToe players."""

import json
from pathlib import Path

DEFAULT_RATING = 1000
K_FACTOR = 32


class EloRating:
    """
    ELO rating system to track player skill levels.

    Uses standard ELO formula with K-factor of 32.
    Ratings are persisted to a JSON file.
    """

    def __init__(self, filepath: str = "ratings.json"):
        """
        Initialize the ELO rating system.

        Args:
            filepath: Path to JSON file for storing ratings
        """
        self.filepath = Path(filepath)
        self.ratings = self._load()

    def _load(self) -> dict:
        """Load ratings from file."""
        if self.filepath.exists():
            try:
                return json.loads(self.filepath.read_text())
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save(self):
        """Save ratings to file."""
        self.filepath.write_text(json.dumps(self.ratings, indent=2))

    def get_rating(self, player_name: str) -> float:
        """Get rating for a player (default: 1000)."""
        return self.ratings.get(player_name, DEFAULT_RATING)

    def set_rating(self, player_name: str, rating: float):
        """Set rating for a player."""
        self.ratings[player_name] = rating

    def get_all_ratings(self) -> dict:
        """Get all player ratings sorted by rating (descending)."""
        return dict(sorted(self.ratings.items(), key=lambda x: x[1], reverse=True))

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for player A against player B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update(self, player1: str, player2: str, result: int) -> tuple:
        """
        Update ratings after a game.

        Args:
            player1: Name of first player
            player2: Name of second player
            result: 1 if player1 wins, -1 if player2 wins, 0 for draw

        Returns:
            Tuple of (player1_change, player2_change)
        """
        r1 = self.get_rating(player1)
        r2 = self.get_rating(player2)

        # Expected scores
        e1 = self.expected_score(r1, r2)
        e2 = 1 - e1

        # Actual scores
        s1, s2 = {1: (1, 0), -1: (0, 1)}.get(result, (0.5, 0.5))

        # Calculate rating changes
        change1 = K_FACTOR * (s1 - e1)
        change2 = K_FACTOR * (s2 - e2)

        # Update ratings
        self.ratings[player1] = r1 + change1
        self.ratings[player2] = r2 + change2

        return (change1, change2)

    def print_leaderboard(self, top_n: int = None):
        """Print a leaderboard of all players."""
        ratings = self.get_all_ratings()
        if not ratings:
            print("No ratings recorded yet.")
            return

        print("\n" + "=" * 40)
        print("ELO Leaderboard")
        print("=" * 40)

        items = list(ratings.items())
        if top_n:
            items = items[:top_n]

        for rank, (name, rating) in enumerate(items, 1):
            print(f"  {rank}. {name}: {rating:.0f}")
        print("=" * 40)
