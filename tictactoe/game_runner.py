from tictactoe.game_engine import TicTacToeGame, clear
from tictactoe.player_interface import Player


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

    def play_game(self, player1: Player, player2: Player, display_board: bool = False) -> int:
        """
        Play a single game between two players.

        Args:
            player1: First player (plays as -1)
            player2: Second player (plays as 1)
            display_board: Whether to display the board after each move

        Returns:
            Winner: -1 (player1), 1 (player2), or 0 (draw)
        """
        game = TicTacToeGame(size=self.size, win_length=self.win_length)
        players = {-1: player1, 1: player2}

        if self.verbose and display_board:
            clear()
            # print("\n" * 2)
            print(f"{'='*50}")
            print(f"{player1.name} (X) vs {player2.name} (O)")
            print(f"{'='*50}")
            game.display()

        move_count = 0
        while not game.game_over:
            current_player = players[game.current_player]
            valid_moves = game.get_valid_moves()

            if not valid_moves:
                break

            try:
                row, col = current_player.get_move(game.get_board_copy(), valid_moves)

                if not game.make_move(row, col):
                    if self.verbose:
                        print(f"Invalid move by {current_player.name}: ({row}, {col})")
                    return -game.current_player  # Opponent wins on invalid move

                move_count += 1

                if self.verbose and display_board:
                    clear()
                    print("\n" * 2)
                    print(f"{'='*50}")
                    print(f"{player1.name} (X) vs {player2.name} (O)")
                    print(f"{'='*50}")
                    symbol = 'X' if game.current_player == 1 else 'O'  # Opposite since we switched
                    print(f"Move {move_count}: {current_player.name} plays ({row}, {col})")
                    game.display()

            except Exception as e:
                if self.verbose:
                    print(f"Error from {current_player.name}: {e}")
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

        return game.winner

    def play_tournament(self, player1: Player, player2: Player, num_games: int) -> dict:
        """
        Play multiple games between two players.

        Args:
            player1: First player
            player2: Second player
            num_games: Number of games to play

        Returns:
            Dictionary with tournament statistics
        """
        results = {
            'player1_wins': 0,
            'player2_wins': 0,
            'draws': 0,
            'games': num_games
        }

        if self.verbose:
            print(f"\nStarting tournament: {player1.name} vs {player2.name}")
            print(f"Playing {num_games} games on {self.size}x{self.size} board")
            print(f"Win length: {self.win_length if self.win_length else self.size}")
            print("-" * 50)

        for game_num in range(num_games):
            # Alternate who goes first
            if game_num % 2 == 0:
                winner = self.play_game(player1, player2, display_board=False)
            else:
                winner = self.play_game(player2, player1, display_board=False)
                # Flip winner since players are swapped
                if winner != 0:
                    winner = -winner

            if winner == -1:
                results['player1_wins'] += 1
            elif winner == 1:
                results['player2_wins'] += 1
            else:
                results['draws'] += 1

            if self.verbose and (game_num + 1) % max(1, num_games // 10) == 0:
                print(f"Progress: {game_num + 1}/{num_games} games completed")

        if self.verbose:
            print("-" * 50)
            print(f"\nTournament Results:")
            print(f"{player1.name}: {results['player1_wins']} wins ({results['player1_wins']/num_games*100:.1f}%)")
            print(f"{player2.name}: {results['player2_wins']} wins ({results['player2_wins']/num_games*100:.1f}%)")
            print(f"Draws: {results['draws']} ({results['draws']/num_games*100:.1f}%)")

        return results
