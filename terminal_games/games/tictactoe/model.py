"""Tic Tac Toe game logic — no UI dependencies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TicTacToeModel:
    """3×3 Tic Tac Toe board state for two local players."""

    board: list[list[str]]
    current_player: str
    cursor_row: int
    cursor_col: int
    winner: str | None
    draw: bool
    game_over: bool

    @classmethod
    def new(cls) -> TicTacToeModel:
        return cls(
            board=[[" ", " ", " "] for _ in range(3)],
            current_player="X",
            cursor_row=1,
            cursor_col=1,
            winner=None,
            draw=False,
            game_over=False,
        )

    def reset(self) -> None:
        fresh = TicTacToeModel.new()
        self.board = fresh.board
        self.current_player = fresh.current_player
        self.cursor_row = fresh.cursor_row
        self.cursor_col = fresh.cursor_col
        self.winner = fresh.winner
        self.draw = fresh.draw
        self.game_over = fresh.game_over

    def move_cursor(self, drow: int, dcol: int) -> None:
        self.cursor_row = (self.cursor_row + drow) % 3
        self.cursor_col = (self.cursor_col + dcol) % 3

    def place(self) -> bool:
        """Place the current player's mark at the cursor. Returns True if the move was made."""
        if self.game_over:
            return False
        if self.board[self.cursor_row][self.cursor_col] != " ":
            return False
        self.board[self.cursor_row][self.cursor_col] = self.current_player
        if self._check_win():
            self.winner = self.current_player
            self.game_over = True
        elif self._check_draw():
            self.draw = True
            self.game_over = True
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
        return True

    def _check_win(self) -> bool:
        b = self.board
        p = self.current_player
        for row in b:
            if all(c == p for c in row):
                return True
        for col in range(3):
            if all(b[row][col] == p for row in range(3)):
                return True
        if all(b[i][i] == p for i in range(3)):
            return True
        if all(b[i][2 - i] == p for i in range(3)):
            return True
        return False

    def _check_draw(self) -> bool:
        return all(self.board[row][col] != " " for row in range(3) for col in range(3))

    def render_lines(self) -> list[str]:
        """Return a plain ASCII representation of the board (3 lines)."""
        return ["".join(row) for row in self.board]
