import time
import numpy as np
from tictactoe.game_engine import TicTacToeGame, clear
from tictactoe.player_interface import Player


class TimingStats:
    """Track move timing statistics for a player."""
    def __init__(self):
        self.move_times = []

    def record(self, elapsed: float):
        self.move_times.append(elapsed)

    def get_summary(self) -> dict:
        if not self.move_times:
            return {"avg": 0, "min": 0, "max": 0, "total": 0, "moves": 0}
        total = sum(self.move_times)
        return {
            "avg": total / len(self.move_times),
            "min": min(self.move_times),
            "max": max(self.move_times),
            "total": total,
            "moves": len(self.move_times),
        }


class GameStats:
    """Track game statistics across a tournament."""
    def __init__(self):
        self.games_played = 0
        self.total_moves = 0
        self.move_counts = []
        self.p1_wins_as_first = 0
        self.p1_wins_as_second = 0
        self.p2_wins_as_first = 0
        self.p2_wins_as_second = 0
        self.draws = 0
        self.timing = {}  # player_name -> TimingStats

    def record_game(self, winner: int, moves: int, p1_went_first: bool):
        self.games_played += 1
        self.total_moves += moves
        self.move_counts.append(moves)

        if winner == -1:  # Player 1 wins
            if p1_went_first:
                self.p1_wins_as_first += 1
            else:
                self.p1_wins_as_second += 1
        elif winner == 1:  # Player 2 wins
            if p1_went_first:
                self.p2_wins_as_second += 1
            else:
                self.p2_wins_as_first += 1
        else:
            self.draws += 1

    def record_move_time(self, player_name: str, elapsed: float):
        if player_name not in self.timing:
            self.timing[player_name] = TimingStats()
        self.timing[player_name].record(elapsed)

    def get_first_move_advantage(self) -> float:
        """Calculate win rate when going first."""
        first_mover_wins = self.p1_wins_as_first + self.p2_wins_as_first
        total_decisive = self.games_played - self.draws
        if total_decisive == 0:
            return 0.0
        return first_mover_wins / total_decisive * 100

    def get_summary(self) -> dict:
        if self.games_played == 0:
            return {}
        return {
            "games": self.games_played,
            "avg_moves": self.total_moves / self.games_played,
            "min_moves": min(self.move_counts) if self.move_counts else 0,
            "max_moves": max(self.move_counts) if self.move_counts else 0,
            "first_move_advantage": self.get_first_move_advantage(),
            "draw_rate": self.draws / self.games_played * 100,
            "p1_wins_as_first": self.p1_wins_as_first,
            "p1_wins_as_second": self.p1_wins_as_second,
            "p2_wins_as_first": self.p2_wins_as_first,
            "p2_wins_as_second": self.p2_wins_as_second,
        }

    def print_summary(self, player1_name: str, player2_name: str):
        summary = self.get_summary()
        if not summary:
            return

        print("\n" + "=" * 50)
        print("Game Statistics:")
        print("=" * 50)
        print(f"  Games played: {summary['games']}")
        print(f"  Average game length: {summary['avg_moves']:.1f} moves")
        print(f"  Shortest game: {summary['min_moves']} moves")
        print(f"  Longest game: {summary['max_moves']} moves")
        print(f"  First-move win rate: {summary['first_move_advantage']:.1f}%")
        print(f"  Draw rate: {summary['draw_rate']:.1f}%")

        print("\n" + "-" * 50)
        print("Timing Statistics:")
        print("-" * 50)
        for name in [player1_name, player2_name]:
            if name in self.timing:
                ts = self.timing[name].get_summary()
                print(f"  {name}:")
                print(f"    avg={ts['avg']:.4f}s, min={ts['min']:.4f}s, max={ts['max']:.4f}s, total={ts['total']:.2f}s")


class RoundRobinStats:
    """Aggregate statistics across all matchups in a round-robin tournament."""

    def __init__(self):
        self.matchup_results = {}  # (p1_name, p2_name) -> {'p1_wins': X, 'p2_wins': Y, 'draws': Z}
        self.player_totals = {}    # player_name -> {'wins': X, 'losses': Y, 'draws': Z, 'games': N}
        self.total_games = 0

    def record_matchup(self, p1_name: str, p2_name: str, p1_wins: int, p2_wins: int, draws: int):
        """Record results of a matchup between two players."""
        self.matchup_results[(p1_name, p2_name)] = {
            'p1_wins': p1_wins,
            'p2_wins': p2_wins,
            'draws': draws
        }

        total = p1_wins + p2_wins + draws
        self.total_games += total

        # Update player totals
        for name in [p1_name, p2_name]:
            if name not in self.player_totals:
                self.player_totals[name] = {'wins': 0, 'losses': 0, 'draws': 0, 'games': 0}

        self.player_totals[p1_name]['wins'] += p1_wins
        self.player_totals[p1_name]['losses'] += p2_wins
        self.player_totals[p1_name]['draws'] += draws
        self.player_totals[p1_name]['games'] += total

        self.player_totals[p2_name]['wins'] += p2_wins
        self.player_totals[p2_name]['losses'] += p1_wins
        self.player_totals[p2_name]['draws'] += draws
        self.player_totals[p2_name]['games'] += total

    def get_standings(self) -> list:
        """Get player standings sorted by win rate."""
        standings = []
        for name, totals in self.player_totals.items():
            win_rate = totals['wins'] / totals['games'] * 100 if totals['games'] > 0 else 0
            standings.append({
                'name': name,
                'wins': totals['wins'],
                'losses': totals['losses'],
                'draws': totals['draws'],
                'games': totals['games'],
                'win_rate': win_rate
            })
        return sorted(standings, key=lambda x: x['win_rate'], reverse=True)

    def print_summary(self, elo_system=None):
        """Print tournament summary with standings and matchup grid."""
        print("\n" + "=" * 60)
        print("ROUND-ROBIN TOURNAMENT RESULTS")
        print("=" * 60)

        standings = self.get_standings()

        # Print standings table
        print(f"\n{'Rank':<6}{'Player':<20}{'W':<8}{'L':<8}{'D':<8}{'Win %':<10}")
        print("-" * 60)
        for rank, s in enumerate(standings, 1):
            print(f"{rank:<6}{s['name']:<20}{s['wins']:<8}{s['losses']:<8}{s['draws']:<8}{s['win_rate']:.1f}%")

        # Print matchup matrix
        players = [s['name'] for s in standings]
        print(f"\n{'Matchup Results Matrix':^60}")
        print("-" * 60)

        # Header row
        header = "vs".ljust(15) + "".join(p[:10].ljust(12) for p in players)
        print(header)

        for p1 in players:
            row = p1[:15].ljust(15)
            for p2 in players:
                if p1 == p2:
                    row += "-".center(12)
                else:
                    key = (p1, p2) if (p1, p2) in self.matchup_results else (p2, p1)
                    if key in self.matchup_results:
                        result = self.matchup_results[key]
                        if key[0] == p1:
                            score = f"{result['p1_wins']}-{result['p2_wins']}"
                        else:
                            score = f"{result['p2_wins']}-{result['p1_wins']}"
                        row += score.center(12)
                    else:
                        row += "-".center(12)
            print(row)

        # Print ELO standings if available
        if elo_system:
            print("\n" + "-" * 60)
            print("ELO Ratings:")
            print("-" * 60)
            ratings = [(name, elo_system.get_rating(name)) for name in players]
            ratings.sort(key=lambda x: x[1], reverse=True)
            for rank, (name, rating) in enumerate(ratings, 1):
                print(f"  {rank}. {name}: {rating:.0f}")

        print("=" * 60)


class GameRunner:
    """
    Orchestrates matches between players.
    Can run single games or batch tournaments.
    """
    def __init__(self, size: int = 3, win_length: int = None, verbose: bool = True):
        """
        Initialize the game runner.
        Args:
            size: Board size
            win_length: Number in a row needed to win
            verbose: Whether to print game progress
        """
        self.size = size
        self.win_length = win_length
        self.verbose = verbose

    def play_game(self, player1: Player, player2: Player, display_board: bool = False,
                  clear_display: bool = True, save_to: str = None,
                  stats: GameStats = None, timeout: float = None,
                  heatmap=None, elo_system=None) -> int:
        """
        Play a single game between two players.
        Args:
            player1: First player (plays as -1 / X)
            player2: Second player (plays as 1 / O)
            display_board: Whether to display the board after each move
            clear_display: Whether to clear terminal before displaying board
            save_to: Optional file path to save game log
            stats: Optional GameStats to record timing and game data
            timeout: Optional max seconds per move (None = no limit)
            heatmap: Optional HeatMapGenerator to record moves
            elo_system: Optional EloRating system to update ratings
        Returns:
            Winner: -1 (player1), 1 (player2), or 0 (draw)
        """
        game = TicTacToeGame(size=self.size, win_length=self.win_length)
        players = {-1: player1, 1: player2}
        move_history_for_heatmap = []  # Track moves for heatmap
        # Ensure players can access the actual win length for this game
        player1.win_length = game.win_length
        player2.win_length = game.win_length

        if self.verbose and display_board:
            if clear_display:
                clear()
            print(f"{'='*50}")
            print(f"{player1.name} (X) vs {player2.name} (O)")
            print(f"{'='*50}")
            game.display(clear_screen=False)

        move_count = 0
        while not game.game_over:
            current_player_obj = players[game.current_player]
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break

            # Convert to tuple to make it immutable
            valid_moves_immutable = tuple(valid_moves)

            try:
                start_time = time.perf_counter()
                move = current_player_obj.get_move(game.get_immutable_board(), valid_moves_immutable)
                elapsed = time.perf_counter() - start_time

                # Validate move format: must be a tuple/list of exactly 2 integers
                if not isinstance(move, (tuple, list)) or len(move) != 2:
                    if self.verbose:
                        print(f"Invalid move format by {current_player_obj.name}: expected (row, col), got {move}")
                    return -game.current_player  # Opponent wins on invalid move format

                row, col = move
                if not isinstance(row, (int, np.integer)) or not isinstance(col, (int, np.integer)):
                    if self.verbose:
                        print(f"Invalid move type by {current_player_obj.name}: row and col must be integers, got ({type(row).__name__}, {type(col).__name__})")
                    return -game.current_player  # Opponent wins on invalid type

                row, col = int(row), int(col)

                # Record timing
                if stats:
                    stats.record_move_time(current_player_obj.name, elapsed)

                # Check timeout
                if timeout and elapsed > timeout:
                    if self.verbose:
                        print(f"Timeout: {current_player_obj.name} took {elapsed:.2f}s (limit: {timeout}s)")
                    return -game.current_player  # Opponent wins on timeout

                if not game.make_move(row, col):
                    if self.verbose:
                        print(f"Invalid move by {current_player_obj.name}: ({row}, {col})")
                    return -game.current_player  # Opponent wins on invalid move

                # Record move for heatmap
                if heatmap:
                    move_history_for_heatmap.append((row, col, game.current_player))

                move_count += 1
                if self.verbose and display_board:
                    if clear_display:
                        clear()
                    print("\n" * 2)
                    print(f"{'='*50}")
                    print(f"{player1.name} (X) vs {player2.name} (O)")
                    print(f"{'='*50}")
                    played_symbol = 'X' if game.current_player == 1 else 'O'
                    print(f"Move {move_count}: {current_player_obj.name} plays ({row}, {col}) as {played_symbol}")
                    game.display(clear_screen=False)

            except Exception as e:
                if self.verbose:
                    print(f"Error from {current_player_obj.name}: {e}")
                return -game.current_player  # Opponent wins on error

        # Notify players of result
        player1.game_over(game.winner)
        player2.game_over(game.winner)

        if self.verbose and display_board:
            if game.winner == 0:
                print("Game ended in a draw!")
            else:
                winner_name = players[game.winner].name
                print(f"{winner_name} wins!")
            print(f"{'='*50}\n")

        if save_to:
            self._save_game_log(game, player1, player2, save_to)

        # Record moves to heatmap
        if heatmap:
            for row, col, player_id in move_history_for_heatmap:
                # Determine if this move was part of a winning game for the player
                is_winning = (game.winner == player_id) if game.winner != 0 else None
                heatmap.record_move(row, col, player_id, is_winning)

        # Update ELO ratings
        if elo_system:
            # Convert winner to ELO format: 1=p1 wins, 0=draw, -1=p2 wins
            if game.winner == -1:
                elo_result = 1
            elif game.winner == 1:
                elo_result = -1
            else:
                elo_result = 0
            elo_system.update(player1.name, player2.name, elo_result)

        # Store move count for stats tracking
        self._last_game_moves = move_count

        return game.winner

    def _save_game_log(self, game: TicTacToeGame, player1: Player, player2: Player, filepath: str):
        """Save a detailed game log with board states after each move."""
        symbols = {-1: 'X', 0: '.', 1: 'O'}
        win_length = self.win_length or game.win_length

        with open(filepath, 'w') as f:
            f.write("Tic-Tac-Toe Game Log\n")
            f.write(f"{'='*50}\n\n")
            f.write("Game Settings:\n")
            f.write(f" Board Size: {self.size}x{self.size}\n")
            f.write(f" Win Length: {win_length}\n\n")
            f.write("Players:\n")
            f.write(f" Player 1 (X): {player1.name}\n")
            f.write(f" Player 2 (O): {player2.name}\n\n")
            f.write(f"{'='*50}\n\n")

            # Initial empty board
            f.write("Initial Board:\n\n")
            self._write_board(f, np.zeros((self.size, self.size), dtype=int), symbols)
            f.write(f"\n{'='*50}\n\n")

            # Board after each move
            board = np.zeros((self.size, self.size), dtype=int)
            for move_num, (row, col, player) in enumerate(game.move_history, 1):
                board[row, col] = player
                player_name = player1.name if player == -1 else player2.name
                symbol = symbols[player]
                f.write(f"Move {move_num}: {player_name} ({symbol}) plays at ({row}, {col})\n\n")
                self._write_board(f, board, symbols, highlight=(row, col))
                f.write(f"\n{'='*50}\n\n")

            # Result
            f.write("Result:\n")
            if game.winner == 0:
                f.write(" Draw\n")
            elif game.winner == -1:
                f.write(f" Winner: {player1.name} (X)\n")
            else:
                f.write(f" Winner: {player2.name} (O)\n")
            f.write(f" Total Moves: {len(game.move_history)}\n")

    def _write_board(self, f, board: np.ndarray, symbols: dict, highlight=None):
        """Write a plain-text board state to file with consistent 3-character cells."""
        col_width = 2 if self.size <= 26 else 3

        # Column numbers
        f.write(" ")
        for col in range(self.size):
            f.write(f"{col:{col_width}} ")
        f.write("\n")

        # Rows
        for row in range(self.size):
            f.write(f"{row:{col_width}} ")
            for col in range(self.size):
                symbol = symbols[board[row, col]]
                if highlight and (row, col) == highlight:
                    cell = f"*{symbol}*"
                else:
                    cell = f" {symbol} "
                f.write(cell)
            f.write("\n")

    def play_tournament(self, player1: Player, player2: Player, num_games: int,
                        timeout: float = None, elo_system=None, heatmap=None,
                        show_stats: bool = True) -> dict:
        """
        Play multiple games, alternating who starts first.
        Args:
            player1: First player
            player2: Second player
            num_games: Number of games to play
            timeout: Optional max seconds per move
            elo_system: Optional EloRating system
            heatmap: Optional HeatMapGenerator
            show_stats: Whether to show detailed statistics
        Returns:
            Results dictionary
        """
        results = {
            'player1_wins': 0,
            'player2_wins': 0,
            'draws': 0,
            'games': num_games
        }

        stats = GameStats()

        # Store initial ELO ratings
        initial_elo = {}
        if elo_system:
            initial_elo[player1.name] = elo_system.get_rating(player1.name)
            initial_elo[player2.name] = elo_system.get_rating(player2.name)

        if self.verbose:
            print(f"\nStarting tournament: {player1.name} vs {player2.name}")
            print(f"Playing {num_games} games on {self.size}x{self.size} board")
            print(f"Win length: {self.win_length or self.size}")
            if timeout:
                print(f"Timeout: {timeout}s per move")
            print("-" * 50)

        progress_interval = max(1, num_games // 10)
        for game_num in range(num_games):
            p1_goes_first = (game_num % 2 == 0)

            if p1_goes_first:
                winner = self.play_game(player1, player2, display_board=False,
                                        stats=stats, timeout=timeout,
                                        heatmap=heatmap, elo_system=elo_system)
            else:
                winner = self.play_game(player2, player1, display_board=False,
                                        stats=stats, timeout=timeout,
                                        heatmap=heatmap, elo_system=elo_system)
                if winner != 0:
                    winner = -winner

            # Record game stats (move count stored by play_game)
            move_count = getattr(self, '_last_game_moves', 0)
            stats.record_game(winner, move_count, p1_goes_first)

            if winner == -1:
                results['player1_wins'] += 1
            elif winner == 1:
                results['player2_wins'] += 1
            else:
                results['draws'] += 1

            if self.verbose and (game_num + 1) % progress_interval == 0:
                print(f"Progress: {game_num + 1}/{num_games} games completed")

        if self.verbose:
            print("-" * 50)
            print(f"\nTournament Results:")
            print(f"{player1.name}: {results['player1_wins']} wins ({results['player1_wins']/num_games*100:.1f}%)")
            print(f"{player2.name}: {results['player2_wins']} wins ({results['player2_wins']/num_games*100:.1f}%)")
            print(f"Draws: {results['draws']} ({results['draws']/num_games*100:.1f}%)")

            # Show ELO changes
            if elo_system:
                print("\n" + "-" * 50)
                print("ELO Ratings:")
                print("-" * 50)
                for name in [player1.name, player2.name]:
                    old_rating = initial_elo[name]
                    new_rating = elo_system.get_rating(name)
                    change = new_rating - old_rating
                    sign = "+" if change >= 0 else ""
                    print(f"  {name}: {old_rating:.0f} → {new_rating:.0f} ({sign}{change:.0f})")

            # Show detailed stats
            if show_stats:
                stats.print_summary(player1.name, player2.name)

        # Save ELO ratings
        if elo_system:
            elo_system.save()

        # Generate heatmap
        if heatmap:
            heatmap.generate()

        return results

    def play_round_robin_tournament(self, participants_config: list, games_per_matchup: int,
                                     create_player_func, timeout: float = None,
                                     elo_system=None, heatmap=None,
                                     show_stats: bool = True) -> dict:
        """
        Play a round-robin tournament where each pair of participants plays against each other.

        Args:
            participants_config: List of participant configuration dicts
            games_per_matchup: Number of games each pair plays
            create_player_func: Function to create a player from config entry (participant, player_id, win_length)
            timeout: Optional max seconds per move
            elo_system: Optional EloRating system
            heatmap: Optional HeatMapGenerator
            show_stats: Whether to show detailed statistics

        Returns:
            Results dictionary with standings and matchup details
        """
        from itertools import combinations

        num_participants = len(participants_config)
        num_matchups = num_participants * (num_participants - 1) // 2

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"ROUND-ROBIN TOURNAMENT")
            print(f"{'='*60}")
            print(f"Participants: {num_participants}")
            print(f"Total matchups: {num_matchups}")
            print(f"Games per matchup: {games_per_matchup}")
            print(f"Total games: {num_matchups * games_per_matchup}")
            print(f"Board size: {self.size}x{self.size}")
            print(f"Win length: {self.win_length or self.size}")
            if timeout:
                print(f"Timeout: {timeout}s per move")
            print(f"{'='*60}\n")

        rr_stats = RoundRobinStats()
        matchup_num = 0

        effective_win_length = TicTacToeGame(size=self.size, win_length=self.win_length).win_length

        # Generate all pairings
        for p1_config, p2_config in combinations(participants_config, 2):
            matchup_num += 1

            # Create fresh player instances for each matchup
            player1 = create_player_func(p1_config, -1, effective_win_length)
            player2 = create_player_func(p2_config, 1, effective_win_length)

            if self.verbose:
                print(f"\n--- Matchup {matchup_num}/{num_matchups}: {player1.name} vs {player2.name} ---")

            # Use existing play_tournament for each matchup
            results = self.play_tournament(
                player1, player2, games_per_matchup,
                timeout=timeout, elo_system=elo_system,
                heatmap=heatmap, show_stats=False  # Defer stats to aggregate summary
            )

            # Record to round-robin stats
            rr_stats.record_matchup(
                player1.name, player2.name,
                results['player1_wins'], results['player2_wins'], results['draws']
            )

        # Print aggregate summary
        if self.verbose and show_stats:
            rr_stats.print_summary(elo_system)

        return {
            'standings': rr_stats.get_standings(),
            'matchups': rr_stats.matchup_results,
            'total_games': rr_stats.total_games
        }
