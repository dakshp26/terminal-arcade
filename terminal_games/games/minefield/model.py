"""Pure Minefield rules: no Textual or Rich imports."""

from __future__ import annotations

import random
from dataclasses import dataclass


_WIDTH = 16
_HEIGHT = 10
_MINES = 25


@dataclass
class MinefieldModel:
    """Grid state for a single-player Minefield game."""

    width: int
    height: int
    mines: int
    board: list[list[int]]       # -1 = mine, 0-8 = adjacent mine count
    revealed: list[list[bool]]
    flagged: list[list[bool]]
    cursor_x: int
    cursor_y: int
    started: bool                 # False until first reveal places mines
    game_over: bool
    won: bool
    flags: int                    # number of flags placed
    revealed_count: int           # number of safe cells uncovered
    death_x: int                  # x of triggered mine (-1 if none yet)
    death_y: int                  # y of triggered mine (-1 if none yet)

    @classmethod
    def new(
        cls,
        width: int = _WIDTH,
        height: int = _HEIGHT,
        mines: int = _MINES,
    ) -> MinefieldModel:
        return cls(
            width=width,
            height=height,
            mines=mines,
            board=[[0] * width for _ in range(height)],
            revealed=[[False] * width for _ in range(height)],
            flagged=[[False] * width for _ in range(height)],
            cursor_x=width // 2,
            cursor_y=height // 2,
            started=False,
            game_over=False,
            won=False,
            flags=0,
            revealed_count=0,
            death_x=-1,
            death_y=-1,
        )

    def reset(self) -> None:
        """Start a fresh game with the same grid dimensions."""
        fresh = MinefieldModel.new(self.width, self.height, self.mines)
        self.board = fresh.board
        self.revealed = fresh.revealed
        self.flagged = fresh.flagged
        self.cursor_x = fresh.cursor_x
        self.cursor_y = fresh.cursor_y
        self.started = fresh.started
        self.game_over = fresh.game_over
        self.won = fresh.won
        self.flags = fresh.flags
        self.revealed_count = fresh.revealed_count
        self.death_x = fresh.death_x
        self.death_y = fresh.death_y

    @property
    def flags_remaining(self) -> int:
        return self.mines - self.flags

    def move_cursor(self, dx: int, dy: int) -> None:
        self.cursor_x = max(0, min(self.width - 1, self.cursor_x + dx))
        self.cursor_y = max(0, min(self.height - 1, self.cursor_y + dy))

    def _place_mines(self, safe_x: int, safe_y: int) -> None:
        """Place mines after the first reveal, keeping a 3×3 safe zone around the cursor."""
        safe: set[tuple[int, int]] = set()
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe.add((nx, ny))

        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in safe
        ]
        # Fallback for tiny grids: only guarantee the clicked cell is safe
        if len(candidates) < self.mines:
            candidates = [
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
                if (x, y) != (safe_x, safe_y)
            ]

        for mx, my in random.sample(candidates, self.mines):
            self.board[my][mx] = -1

        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == -1:
                    continue
                self.board[y][x] = sum(
                    1
                    for dy in range(-1, 2)
                    for dx in range(-1, 2)
                    if 0 <= x + dx < self.width
                    and 0 <= y + dy < self.height
                    and self.board[y + dy][x + dx] == -1
                )

        self.started = True

    def reveal(self) -> None:
        """Reveal the cell at the cursor. No-op if flagged, already revealed, or game over."""
        x, y = self.cursor_x, self.cursor_y
        if self.game_over or self.flagged[y][x] or self.revealed[y][x]:
            return

        if not self.started:
            self._place_mines(x, y)

        if self.board[y][x] == -1:
            self.game_over = True
            self.death_x, self.death_y = x, y
            for ry in range(self.height):
                for rx in range(self.width):
                    if self.board[ry][rx] == -1:
                        self.revealed[ry][rx] = True
        else:
            self._flood_reveal(x, y)
            self._check_win()

    def _flood_reveal(self, x: int, y: int) -> None:
        """Reveal a cell; if it has 0 adjacent mines, spread to all neighbours."""
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if self.revealed[cy][cx] or self.flagged[cy][cx]:
                continue
            self.revealed[cy][cx] = True
            self.revealed_count += 1
            if self.board[cy][cx] == 0:
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = cx + dx, cy + dy
                        if (
                            0 <= nx < self.width
                            and 0 <= ny < self.height
                            and not self.revealed[ny][nx]
                        ):
                            stack.append((nx, ny))

    def _check_win(self) -> None:
        if self.revealed_count >= self.width * self.height - self.mines:
            self.won = True
            self.game_over = True

    def toggle_flag(self) -> None:
        """Toggle a flag on the cell at the cursor. No-op if revealed or game over."""
        x, y = self.cursor_x, self.cursor_y
        if self.game_over or self.revealed[y][x]:
            return
        if self.flagged[y][x]:
            self.flagged[y][x] = False
            self.flags -= 1
        else:
            self.flagged[y][x] = True
            self.flags += 1

    def render_lines(self) -> list[str]:
        """One ASCII character per cell; used for testing and as panel input."""
        lines: list[str] = []
        for y in range(self.height):
            row: list[str] = []
            for x in range(self.width):
                if self.revealed[y][x]:
                    v = self.board[y][x]
                    if v == -1:
                        row.append("!" if x == self.death_x and y == self.death_y else "*")
                    elif v == 0:
                        row.append(".")
                    else:
                        row.append(str(v))
                elif self.flagged[y][x]:
                    row.append("F")
                else:
                    row.append("#")
            lines.append("".join(row))
        return lines
