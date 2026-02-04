#!/usr/bin/env python3
"""
Tic-Tac-Toe Game Runner
Supports AI vs AI, Human vs AI, and Human vs Human matches.
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from tictactoe.game_runner import GameRunner
from tictactoe.human_player import HumanPlayer
from tictactoe.players.random_player import RandomPlayer
from tictactoe.players.minimax_player import MinimaxPlayer

DEFAULT_TOURNAMENT_CONFIG = "tournament_participants.json"
PLAYER_TYPE_TO_CLASS = {
    'human': HumanPlayer,
    'random': RandomPlayer,
    'minimax': MinimaxPlayer,
}
DEFAULT_PLAYER_NAMES = {
    'human': "Human Player {num}",
    'random': "Random AI",
    'minimax': "Minimax AI",
}


def load_custom_player(filepath: str, player_id: int, win_length: int | None):
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
    return PlayerClass(name=path.stem, player_id=player_id, win_length=win_length)


def create_player(player_type: str, player_id: int, player_name: str = None, win_length: int | None = None):
    """Create player instance by type."""
    lowered = player_type.lower()
    if lowered in PLAYER_TYPE_TO_CLASS:
        cls = PLAYER_TYPE_TO_CLASS[lowered]
        default_name = DEFAULT_PLAYER_NAMES[lowered]
        if lowered == 'human':
            default_name = default_name.format(num=1 if player_id == -1 else 2)
        name = player_name or default_name
        return cls(name=name, player_id=player_id, win_length=win_length)
    return load_custom_player(player_type, player_id, win_length)


def load_tournament_config(filepath: str) -> dict:
    """Load tournament configuration from JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Tournament config file not found: {filepath}")

    with open(path, 'r') as f:
        config = json.load(f)

    # Validate required fields
    if 'participants' not in config:
        raise ValueError("Tournament config must contain 'participants' array")

    if len(config['participants']) < 2:
        raise ValueError("Tournament requires at least 2 participants")

    for i, p in enumerate(config['participants']):
        if 'name' not in p:
            raise ValueError(f"Participant {i} missing required 'name' field")
        if 'type' not in p:
            raise ValueError(f"Participant {i} missing required 'type' field")
        if p['type'] == 'custom' and 'file' not in p:
            raise ValueError(f"Participant '{p['name']}' has type 'custom' but missing 'file' field")

    return config


def create_player_from_config(participant: dict, player_id: int, win_length: int | None):
    """Create a player instance from a tournament config participant entry."""
    ptype = participant['type'].lower()
    name = participant['name']

    if ptype == 'custom':
        player = load_custom_player(participant['file'], player_id, win_length)
        player.name = name  # Override with config name
        return player
    else:
        return create_player(ptype, player_id, name, win_length)


def _resolve_win_length(size: int, win_length: int | None) -> int:
    return win_length or (size if size <= 5 else 5)


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
    parser.add_argument('--player1', default=None,
                        help='Player 1: human, random, minimax, or path to custom player file')
    parser.add_argument('--player2', default=None,
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

    # Analytics flags
    parser.add_argument('--timeout', type=float, default=None,
                        help='Max seconds per move (disqualify on timeout)')
    parser.add_argument('--elo', action='store_true',
                        help='Enable ELO rating tracking')
    parser.add_argument('--elo-file', type=str, default='ratings.json',
                        help='Path to ELO ratings file (default: ratings.json)')
    parser.add_argument('--heatmap', action='store_true',
                        help='Generate move heat map after tournament')
    parser.add_argument('--heatmap-output', type=str, default='heatmap.png',
                        help='Heat map output path (default: heatmap.png)')
    parser.add_argument('--no-stats', action='store_true',
                        help='Disable detailed statistics output')
    parser.add_argument('--leaderboard', action='store_true',
                        help='Show ELO leaderboard and exit')
    parser.add_argument('--tournament-config', type=str, default=None,
                        help=f'Path to JSON file with tournament participants (default: {DEFAULT_TOURNAMENT_CONFIG} when no players are specified)')

    args = parser.parse_args()

    # Default to repository tournament config when no players are specified
    if args.tournament_config is None and not args.player1 and not args.player2:
        default_config_path = Path(DEFAULT_TOURNAMENT_CONFIG)
        if default_config_path.exists():
            args.tournament_config = str(default_config_path)

    # Handle leaderboard display
    if args.leaderboard:
        from tictactoe.rating import EloRating
        elo = EloRating(args.elo_file)
        elo.print_leaderboard()
        return

    # Handle multi-participant tournament from config file
    if args.tournament_config:
        if args.player1 or args.player2:
            parser.error("--tournament-config cannot be used with --player1/--player2")

        try:
            config = load_tournament_config(args.tournament_config)

            verbose = not args.quiet
            runner = GameRunner(size=args.size, win_length=args.win_length, verbose=verbose)

            # Initialize analytics systems
            elo_system = None
            heatmap = None

            if args.elo:
                from tictactoe.rating import EloRating
                elo_system = EloRating(args.elo_file)

            if args.heatmap:
                from tictactoe.visualization import HeatMapGenerator
                heatmap = HeatMapGenerator(args.size, args.heatmap_output)

            # Determine games per matchup
            games_per_matchup = args.games if args.games > 1 else config.get('games_per_matchup', 10)

            # Run round-robin tournament
            runner.play_round_robin_tournament(
                participants_config=config['participants'],
                games_per_matchup=games_per_matchup,
                create_player_func=create_player_from_config,
                timeout=args.timeout,
                elo_system=elo_system,
                heatmap=heatmap,
                show_stats=not args.no_stats
            )

            # Save ELO (heatmap is already generated in play_round_robin_tournament via play_tournament)
            if elo_system:
                elo_system.save()

            return
        except KeyboardInterrupt:
            print("\n\nTournament interrupted by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate required arguments for game play
    if not args.player1 or not args.player2:
        parser.error("--player1 and --player2 are required when playing games")

    try:
        effective_win_length = _resolve_win_length(args.size, args.win_length)
        player1 = create_player(args.player1, -1, args.name1, effective_win_length)
        player2 = create_player(args.player2, 1, args.name2, effective_win_length)

        verbose = not args.quiet
        runner = GameRunner(size=args.size, win_length=args.win_length, verbose=verbose)

        # Initialize analytics systems
        elo_system = None
        heatmap = None

        if args.elo:
            from tictactoe.rating import EloRating
            elo_system = EloRating(args.elo_file)

        if args.heatmap:
            from tictactoe.visualization import HeatMapGenerator
            heatmap = HeatMapGenerator(args.size, args.heatmap_output)

        if args.games == 1:
            # Single game mode
            from tictactoe.game_runner import GameStats
            stats = GameStats() if not args.no_stats else None

            winner = runner.play_game(
                player1, player2,
                display_board=args.display or verbose,
                clear_display=not args.no_clear,
                save_to=args.save_to,
                stats=stats,
                timeout=args.timeout,
                heatmap=heatmap,
                elo_system=elo_system
            )

            if verbose:
                if winner == -1:
                    print(f"\n{player1.name} wins!")
                elif winner == 1:
                    print(f"\n{player2.name} wins!")
                else:
                    print("\nGame ended in a draw!")

                # Show timing for single game
                if stats and not args.no_stats:
                    stats.print_summary(player1.name, player2.name)

                # Show ELO changes for single game
                if elo_system:
                    print("\nELO Ratings updated.")
                    elo_system.save()

            # Generate heatmap for single game
            if heatmap:
                heatmap.generate()
        else:
            # Tournament mode
            results = runner.play_tournament(
                player1, player2, args.games,
                timeout=args.timeout,
                elo_system=elo_system,
                heatmap=heatmap,
                show_stats=not args.no_stats
            )

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
