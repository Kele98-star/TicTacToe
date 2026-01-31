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

    def play_game(self, player1: Player, player2: Player, display_board: bool = False,
                  clear_display: bool = True, save_to: str = None) -> int:
        """
        Play a single game between two players.

        Args:
            player1: First player (plays as -1)
            player2: Second player (plays as 1)
            display_board: Whether to display the board after each move
            clear_display: Whether to clear terminal before displaying board
            save_to: Optional file path to save game log

        Returns:
            Winner: -1 (player1), 1 (player2), or 0 (draw)
        """
        game = TicTacToeGame(size=self.size, win_length=self.win_length)
        players = {-1: player1, 1: player2}

        if self.verbose and display_board:
            if clear_display:
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
                    if clear_display:
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

        # Save game log if requested
        if save_to:
            self._save_game_log(game, player1, player2, save_to)

        return game.winner

    def _save_game_log(self, game, player1: Player, player2: Player, filepath: str):
        """
        Save game log to a file.

        Args:
            game: TicTacToeGame instance
            player1: First player
            player2: Second player
            filepath: Path to save the game log
        """
        import numpy as np

        with open(filepath, 'w') as f:
            f.write(f"Tic-Tac-Toe Game Log\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"Game Settings:\n")
            f.write(f"  Board Size: {self.size}x{self.size}\n")
            f.write(f"  Win Length: {self.win_length if self.win_length else self.size}\n\n")
            f.write(f"Players:\n")
            f.write(f"  Player 1 (X): {player1.name}\n")
            f.write(f"  Player 2 (O): {player2.name}\n\n")
            f.write(f"{'='*50}\n\n")

            symbols = {-1: 'X', 0: '.', 1: 'O'}

            # Write initial empty board
            f.write(f"Initial Board:\n\n")
            self._write_board(f, np.zeros((self.size, self.size), dtype=int), symbols)
            f.write(f"\n{'='*50}\n\n")

            # Reconstruct and write all board states
            board = np.zeros((self.size, self.size), dtype=int)
            for move_num, (row, col, player) in enumerate(game.move_history, 1):
                board[row, col] = player
                player_name = player1.name if player == -1 else player2.name
                symbol = 'X' if player == -1 else 'O'

                f.write(f"Move {move_num}: {player_name} ({symbol}) plays at ({row}, {col})\n\n")
                self._write_board(f, board, symbols, highlight=(row, col))
                f.write(f"\n{'='*50}\n\n")

            f.write(f"Result:\n")
            if game.winner == 0:
                f.write(f"  Draw\n")
            elif game.winner == -1:
                f.write(f"  Winner: {player1.name} (X)\n")
            else:
                f.write(f"  Winner: {player2.name} (O)\n")
            f.write(f"  Total Moves: {len(game.move_history)}\n")

    def _write_board(self, f, board, symbols, highlight=None):
        """
        Write a board state to file.

        Args:
            f: File object to write to
            board: Board state (numpy array)
            symbols: Dictionary mapping values to symbols
            highlight: Optional (row, col) tuple to highlight with asterisk
        """
        # Print column numbers
        f.write("   ")
        for col in range(self.size):
            if self.size <= 26:
                f.write(f"{col:2} ")
            else:
                f.write(f"{col:3} ")
        f.write("\n")

        # Print board
        for row in range(self.size):
            if self.size <= 26:
                f.write(f"{row:2} ")
            else:
                f.write(f"{row:3} ")

            for col in range(self.size):
                symbol = symbols[board[row, col]]
                # Add asterisk to highlight the last move
                if highlight and row == highlight[0] and col == highlight[1]:
                    if self.size <= 26:
                        f.write(f"*{symbol}*")
                    else:
                        f.write(f"*{symbol}* ")
                else:
                    if self.size <= 26:
                        f.write(f" {symbol} ")
                    else:
                        f.write(f" {symbol}  ")
            f.write("\n")

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
