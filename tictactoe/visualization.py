"""Visualization tools for TicTacToe analytics."""

import numpy as np


class HeatMapGenerator:
    """
    Generate heat maps showing move frequency patterns.

    Tracks moves across multiple games and generates visual heat maps
    showing popular positions, winning moves, and losing moves.
    """

    def __init__(self, board_size: int, output_path: str = "heatmap.png"):
        """
        Initialize the heat map generator.

        Args:
            board_size: Size of the game board
            output_path: Path to save the generated heat map image
        """
        self.size = board_size
        self.output_path = output_path

        # Track all moves
        self.all_moves = np.zeros((board_size, board_size), dtype=np.float64)

        # Track moves by player
        self.player1_moves = np.zeros((board_size, board_size), dtype=np.float64)
        self.player2_moves = np.zeros((board_size, board_size), dtype=np.float64)

        # Track winning vs losing moves
        self.winning_moves = np.zeros((board_size, board_size), dtype=np.float64)
        self.losing_moves = np.zeros((board_size, board_size), dtype=np.float64)

    def record_move(self, row: int, col: int, player_id: int, is_winning: bool = None):
        """
        Record a move for heat map generation.

        Args:
            row: Row position of the move
            col: Column position of the move
            player_id: Player who made the move (-1 or 1)
            is_winning: True if this was part of a winning game for this player,
                       False if losing, None if draw
        """
        self.all_moves[row, col] += 1

        if player_id == -1:
            self.player1_moves[row, col] += 1
        else:
            self.player2_moves[row, col] += 1

        if is_winning is True:
            self.winning_moves[row, col] += 1
        elif is_winning is False:
            self.losing_moves[row, col] += 1

    def generate(self):
        """Generate and save the heat map image."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.colors as mcolors
        except ImportError:
            print("Heat map generation requires matplotlib.")
            print("Install with: pip install matplotlib")
            return False

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        fig.suptitle(f'Move Heat Maps ({self.size}x{self.size} Board)', fontsize=14)

        # Helper function to add cell values
        def add_annotations(ax, data):
            for i in range(self.size):
                for j in range(self.size):
                    value = data[i, j]
                    if value > 0:
                        text_color = 'white' if value > data.max() * 0.5 else 'black'
                        ax.text(j, i, f'{int(value)}', ha='center', va='center',
                                color=text_color, fontsize=8 if self.size <= 10 else 6)

        # All moves heat map
        ax1 = axes[0, 0]
        im1 = ax1.imshow(self.all_moves, cmap='YlOrRd', interpolation='nearest')
        ax1.set_title('All Moves')
        plt.colorbar(im1, ax=ax1, shrink=0.8)
        if self.size <= 15:
            add_annotations(ax1, self.all_moves)

        # Player comparison (difference)
        ax2 = axes[0, 1]
        diff = self.player1_moves - self.player2_moves
        max_val = max(abs(diff.min()), abs(diff.max())) or 1
        im2 = ax2.imshow(diff, cmap='RdBu', vmin=-max_val, vmax=max_val, interpolation='nearest')
        ax2.set_title('Player 1 (red) vs Player 2 (blue)')
        plt.colorbar(im2, ax=ax2, shrink=0.8)

        # Winning moves heat map
        ax3 = axes[1, 0]
        im3 = ax3.imshow(self.winning_moves, cmap='Greens', interpolation='nearest')
        ax3.set_title('Winning Game Moves')
        plt.colorbar(im3, ax=ax3, shrink=0.8)
        if self.size <= 15:
            add_annotations(ax3, self.winning_moves)

        # Losing moves heat map
        ax4 = axes[1, 1]
        im4 = ax4.imshow(self.losing_moves, cmap='Reds', interpolation='nearest')
        ax4.set_title('Losing Game Moves')
        plt.colorbar(im4, ax=ax4, shrink=0.8)
        if self.size <= 15:
            add_annotations(ax4, self.losing_moves)

        # Add grid lines and labels for small boards
        for ax in axes.flat:
            if self.size <= 15:
                ax.set_xticks(np.arange(self.size))
                ax.set_yticks(np.arange(self.size))
                ax.set_xticklabels(np.arange(self.size))
                ax.set_yticklabels(np.arange(self.size))
            ax.set_xlabel('Column')
            ax.set_ylabel('Row')

        plt.tight_layout()
        plt.savefig(self.output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Heat map saved to {self.output_path}")
        return True

    def get_statistics(self) -> dict:
        """Get statistics about move patterns."""
        stats = {
            "total_moves": int(self.all_moves.sum()),
            "most_played_cell": None,
            "least_played_cell": None,
            "center_preference": 0.0,
            "corner_preference": 0.0,
            "edge_preference": 0.0,
        }

        if stats["total_moves"] == 0:
            return stats

        # Find most/least played cells
        max_idx = np.unravel_index(np.argmax(self.all_moves), self.all_moves.shape)
        min_idx = np.unravel_index(np.argmin(self.all_moves), self.all_moves.shape)
        stats["most_played_cell"] = (int(max_idx[0]), int(max_idx[1]))
        stats["least_played_cell"] = (int(min_idx[0]), int(min_idx[1]))

        # Calculate position preferences
        total = stats["total_moves"]

        # Center (middle cell or middle 4 for even boards)
        center = self.size // 2
        if self.size % 2 == 1:
            center_moves = self.all_moves[center, center]
        else:
            center_moves = (self.all_moves[center-1:center+1, center-1:center+1]).sum()
        stats["center_preference"] = center_moves / total * 100

        # Corners
        corner_moves = (self.all_moves[0, 0] + self.all_moves[0, self.size-1] +
                       self.all_moves[self.size-1, 0] + self.all_moves[self.size-1, self.size-1])
        stats["corner_preference"] = corner_moves / total * 100

        # Edges (excluding corners)
        edge_moves = (self.all_moves[0, 1:-1].sum() + self.all_moves[-1, 1:-1].sum() +
                     self.all_moves[1:-1, 0].sum() + self.all_moves[1:-1, -1].sum())
        stats["edge_preference"] = edge_moves / total * 100

        return stats

    def print_statistics(self):
        """Print move pattern statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 50)
        print("Move Pattern Statistics:")
        print("=" * 50)
        print(f"  Total moves recorded: {stats['total_moves']}")
        if stats['most_played_cell']:
            print(f"  Most played cell: {stats['most_played_cell']}")
            print(f"  Least played cell: {stats['least_played_cell']}")
        print(f"  Center preference: {stats['center_preference']:.1f}%")
        print(f"  Corner preference: {stats['corner_preference']:.1f}%")
        print(f"  Edge preference: {stats['edge_preference']:.1f}%")
