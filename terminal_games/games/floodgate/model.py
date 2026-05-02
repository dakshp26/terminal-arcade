"""Pure Floodgate rules: no Textual or Rich imports."""

from __future__ import annotations

import random
from dataclasses import dataclass

_WIDTH = 20
_HEIGHT = 14
_COLORS = 6
_MAX_MOVES = 30

_DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))


@dataclass
class FloodgateModel:
    """Grid state for a single-player Floodgate game."""

    width: int
    height: int
    colors: int
    max_moves: int
    board: list[list[int]]      # 0 .. colors-1, color index per cell
    owned: list[list[bool]]     # True = part of player's territory
    current_color: int          # color index of the entire owned territory
    moves: int
    game_over: bool
    won: bool

    @classmethod
    def new(
        cls,
        width: int = _WIDTH,
        height: int = _HEIGHT,
        colors: int = _COLORS,
        max_moves: int = _MAX_MOVES,
    ) -> FloodgateModel:
        board = [
            [random.randint(0, colors - 1) for _ in range(width)]
            for _ in range(height)
        ]
        owned = [[False] * width for _ in range(height)]
        start_color = board[0][0]

        # Claim all cells connected to [0,0] that share the starting colour
        stack = [(0, 0)]
        owned[0][0] = True
        while stack:
            x, y = stack.pop()
            for dx, dy in _DIRS:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < width
                    and 0 <= ny < height
                    and not owned[ny][nx]
                    and board[ny][nx] == start_color
                ):
                    owned[ny][nx] = True
                    stack.append((nx, ny))

        return cls(
            width=width,
            height=height,
            colors=colors,
            max_moves=max_moves,
            board=board,
            owned=owned,
            current_color=start_color,
            moves=0,
            game_over=False,
            won=False,
        )

    def reset(self) -> None:
        fresh = FloodgateModel.new(self.width, self.height, self.colors, self.max_moves)
        self.board = fresh.board
        self.owned = fresh.owned
        self.current_color = fresh.current_color
        self.moves = fresh.moves
        self.game_over = fresh.game_over
        self.won = fresh.won

    @property
    def owned_count(self) -> int:
        return sum(1 for y in range(self.height) for x in range(self.width) if self.owned[y][x])

    @property
    def total_cells(self) -> int:
        return self.width * self.height

    def flood(self, color_idx: int) -> None:
        """Flood territory with the chosen colour. No-op if same as current or game over."""
        if self.game_over or color_idx == self.current_color:
            return

        self.current_color = color_idx

        # Re-colour all owned cells
        for y in range(self.height):
            for x in range(self.width):
                if self.owned[y][x]:
                    self.board[y][x] = color_idx

        # Expand: absorb all adjacent unowned cells of the new colour (cascade)
        stack: list[tuple[int, int]] = []
        queued: set[tuple[int, int]] = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.owned[y][x]:
                    for dx, dy in _DIRS:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < self.width
                            and 0 <= ny < self.height
                            and not self.owned[ny][nx]
                            and self.board[ny][nx] == color_idx
                            and (nx, ny) not in queued
                        ):
                            queued.add((nx, ny))
                            stack.append((nx, ny))

        while stack:
            x, y = stack.pop()
            self.owned[y][x] = True
            for dx, dy in _DIRS:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not self.owned[ny][nx]
                    and self.board[ny][nx] == color_idx
                    and (nx, ny) not in queued
                ):
                    queued.add((nx, ny))
                    stack.append((nx, ny))

        self.moves += 1

        if self.owned_count == self.total_cells:
            self.won = True
            self.game_over = True
        elif self.moves >= self.max_moves:
            self.game_over = True

    def render_lines(self) -> list[str]:
        """Owned cells: uppercase A–F. Unowned: lowercase a–f."""
        lines: list[str] = []
        for y in range(self.height):
            row: list[str] = []
            for x in range(self.width):
                c = self.board[y][x]
                row.append(chr(65 + c) if self.owned[y][x] else chr(97 + c))
            lines.append("".join(row))
        return lines
