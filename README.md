# Tic-Tac-Toe Game System

A flexible tic-tac-toe game system that supports:
- AI vs AI matches
- Human vs AI matches
- Human vs Human matches
- Configurable board sizes (3x3 to 100x100+)
- Custom AI players
- Tournament mode (play multiple games)

## Board Representation

The game uses -1, 0, 1 to represent the board:
- `-1`: Player 1 (displayed as 'X')
- `0`: Empty cell (displayed as '.')
- `1`: Player 2 (displayed as 'O')

## Installation

No external dependencies required beyond NumPy:

```bash
pip install numpy
```

## Usage

### Basic Examples

Play 1000 games between two random AIs on a 100x100 board:
```bash
python -m tictactoe.main --player1 random --player2 random --games 1000 --size 100
```

Human vs Minimax AI on a 3x3 board with display:
```bash
python -m tictactoe.main --player1 human --player2 minimax --size 3 --display
```

Two humans playing:
```bash
python -m tictactoe.main --player1 human --player2 human --size 3 --display
```

Custom AI vs Random AI:
```bash
python -m tictactoe.main --player1 example_custom_player.py --player2 random --games 100
```

### Command Line Options

```
--player1 <type>       Player 1: human, random, minimax, or path to custom player file
--player2 <type>       Player 2: human, random, minimax, or path to custom player file
--games <n>           Number of games to play (default: 1)
--size <n>            Board size (default: 3)
--win-length <n>      Number in a row to win (default: 5 for large boards, size for small)
--display             Display board after each move (for single game)
--quiet               Suppress all output except final results
--name1 <name>        Custom name for player 1
--name2 <name>        Custom name for player 2
```

## Creating Custom AI Players

To create your own AI player, create a Python file with a class that inherits from `Player`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from typing import Tuple
from tictactoe.player_interface import Player


class MyCustomPlayer(Player):
    """Your custom AI player."""

    def get_move(self, board: np.ndarray, valid_moves: list) -> Tuple[int, int]:
        """
        Choose a move.

        Args:
            board: Current board state (numpy array with -1, 0, 1)
            valid_moves: List of valid moves as (row, col) tuples

        Returns:
            Chosen move as (row, col)
        """
        # Your logic here
        # self.player_id contains your player ID (-1 or 1)

        # Example: choose first valid move
        return valid_moves[0]

    def game_over(self, winner: int):
        """
        Optional: Called when game ends.
        winner: -1, 1 (player won), or 0 (draw)
        """
        pass
```

See [example_custom_player.py](example_custom_player.py) for complete examples.

## Project Structure

```
tictactoe/
├── __init__.py
├── game_engine.py       # Core game logic
├── player_interface.py  # Abstract player class
├── game_runner.py       # Orchestrates matches
├── human_player.py      # Human player implementation
├── main.py             # Entry point
└── players/
    ├── __init__.py
    ├── random_player.py    # Random move AI
    └── minimax_player.py   # Minimax algorithm AI

example_custom_player.py  # Example custom players
README.md                # This file
```

## Built-in AI Players

### Random Player
Makes random valid moves. Fast and simple.

```bash
python -m tictactoe.main --player1 random --player2 random --games 1000
```

### Minimax Player
Uses minimax algorithm with alpha-beta pruning. Good for small boards (3x3 to 5x5). For larger boards, uses depth-limited search with heuristic evaluation.

```bash
python -m tictactoe.main --player1 minimax --player2 random --size 5
```

## Large Board Considerations

For 100x100 boards:
- Default win condition is 5 in a row (configurable with `--win-length`)
- Minimax AI uses depth-limited search with heuristics
- No time limit on moves - AIs can think as long as needed
- Board display may be large in terminal

## Tournament Results

When running multiple games, the system displays:
- Number of wins for each player
- Number of draws
- Win percentages

Players alternate who goes first to ensure fairness.

## Tips for Creating Strong AI

1. Use board state analysis to evaluate positions
2. Look for winning moves first
3. Block opponent's winning moves
4. Consider strategic positions (center, corners)
5. For large boards, focus on local patterns rather than analyzing the entire board
6. Use heuristics and depth-limited search for efficiency

## License

Free to use and modify.
