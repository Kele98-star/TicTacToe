#!/usr/bin/env python3
"""
Tic-Tac-Toe Game Runner
Supports AI vs AI, Human vs AI, and Human vs Human matches.
"""

import argparse
import importlib.util
import sys
from pathlib import Path

from tictactoe.game_runner import GameRunner
from tictactoe.human_player import HumanPlayer
from tictactoe.players.random_player import RandomPlayer
from tictactoe.players.minimax_player import MinimaxPlayer


def load_custom_player(filepath: str, player_id: int):
    """Load custom player from Python file containing Player subclass."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Player file not found: {filepath}")

    module_name = f"custom_player_{path.stem.replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    from tictactoe.player_interface import Player
    player_classes = [
        obj for name, obj in module.__dict__.items()
        if isinstance(obj, type) and issubclass(obj, Player) and obj != Player
    ]

    if not player_classes:
        raise ValueError(f"No Player subclass found in {filepath}")

    PlayerClass = player_classes[0]
    return PlayerClass(name=path.stem, player_id=player_id)


def create_player(player_type: str, player_id: int, player_name: str = None):
    """Create player instance by type."""
    type_to_class = {
        'human': HumanPlayer,
        'random': RandomPlayer,
        'minimax': MinimaxPlayer,
    }
    lowered = player_type.lower()
    if lowered in type_to_class:
        cls = type_to_class[lowered]
        default_names = {
            'human': f"Human Player {1 if player_id == -1 else 2}",
            'random': "Random AI",
            'minimax': "Minimax AI",
        }
        name = player_name or default_names.get(lowered)
        return cls(name=name, player_id=player_id)
    return load_custom_player(player_type, player_id)


def main():
    parser = argparse.ArgumentParser(
        description='Tic-Tac-Toe Game Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tictactoe.main --player1 random --player2 random --games 1000 --size 100
  python -m tictactoe.main --player1 human --player2 minimax --size 3 --display
  python -m tictactoe.main --player1 my_ai.py --player2 random --games 100
  python -m tictactoe.main --player1 ai1.py --player2 ai2.py --games 1000 --size 100
        """
    )
    parser.add_argument('--player1', required=True,
                        help='Player 1: human, random, minimax, or path to custom player file')
    parser.add_argument('--player2', required=True,
                        help='Player 2: human, random, minimax, or path to custom player file')
    parser.add_argument('--games', type=int, default=1,
                        help='Number of games to play (default: 1)')
    parser.add_argument('--size', type=int, default=3,
                        help='Board size (default: 3)')
    parser.add_argument('--win-length', type=int, default=None,
                        help='Number in a row to win (default: 5 for boards > 5x5, size otherwise)')
    parser.add_argument('--display', action='store_true',
                        help='Display board after each move (only for single game)')
    parser.add_argument('--no-clear', action='store_true',
                        help="Don't clear terminal when displaying board")
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress all output except final results')
    parser.add_argument('--name1', type=str, default=None,
                        help='Custom name for player 1')
    parser.add_argument('--name2', type=str, default=None,
                        help='Custom name for player 2')
    parser.add_argument('--save-to', type=str, default=None,
                        help='Save game log to specified file')

    args = parser.parse_args()

    try:
        player1 = create_player(args.player1, -1, args.name1)
        player2 = create_player(args.player2, 1, args.name2)

        verbose = not args.quiet
        runner = GameRunner(size=args.size, win_length=args.win_length, verbose=verbose)

        if args.games == 1:
            winner = runner.play_game(
                player1, player2,
                display_board=args.display or verbose,
                clear_display=not args.no_clear,
                save_to=args.save_to
            )
            if verbose:
                if winner == -1:
                    print(f"\n{player1.name} wins!")
                elif winner == 1:
                    print(f"\n{player2.name} wins!")
                else:
                    print("\nGame ended in a draw!")
        else:
            results = runner.play_tournament(player1, player2, args.games)
            if not verbose:
                print(f"{player1.name}: {results['player1_wins']}")
                print(f"{player2.name}: {results['player2_wins']}")
                print(f"Draws: {results['draws']}")
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
