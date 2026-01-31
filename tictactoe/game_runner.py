import numpy as np
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
            player1: First player (plays as -1 / X)
            player2: Second player (plays as 1 / O)
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

            try:
                row, col = current_player_obj.get_move(game.get_board_copy(), valid_moves)
                if not game.make_move(row, col):
                    if self.verbose:
                        print(f"Invalid move by {current_player_obj.name}: ({row}, {col})")
                    return -game.current_player  # Opponent wins on invalid move

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

    def play_tournament(self, player1: Player, player2: Player, num_games: int) -> dict:
        """Play multiple games, alternating who starts first."""
        results = {
            'player1_wins': 0,
            'player2_wins': 0,
            'draws': 0,
            'games': num_games
        }

        if self.verbose:
            print(f"\nStarting tournament: {player1.name} vs {player2.name}")
            print(f"Playing {num_games} games on {self.size}x{self.size} board")
            print(f"Win length: {self.win_length or self.size}")
            print("-" * 50)

        for game_num in range(num_games):
            if game_num % 2 == 0:
                winner = self.play_game(player1, player2, display_board=False)
            else:
                winner = self.play_game(player2, player1, display_board=False)
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