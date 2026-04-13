"""Pure Serpentine rules: no Textual or Rich imports."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]


_OPPOSITE: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


@dataclass
class SerpentineModel:
    """Grid state and movement; one ``tick()`` advances the snake one cell."""

    width: int
    height: int
    snake: deque[tuple[int, int]]
    direction: Direction
    food: tuple[int, int]
    score: int = 0
    game_over: bool = False
    _queued_direction: Direction | None = field(default=None, repr=False)

    @classmethod
    def new(cls, width: int = 30, height: int = 15) -> SerpentineModel:
        head_x = width // 2
        head_y = height // 2
        body: deque[tuple[int, int]] = deque()
        for i in range(3):
            body.append((head_x - (2 - i), head_y))
        direction = Direction.RIGHT
        food = cls._random_food(width, height, frozenset(body))
        return cls(
            width=width,
            height=height,
            snake=body,
            direction=direction,
            food=food,
        )

    @staticmethod
    def _random_food(
        width: int,
        height: int,
        occupied: frozenset[tuple[int, int]],
    ) -> tuple[int, int]:
        empty = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if (x, y) not in occupied
        ]
        return random.choice(empty)

    def queue_direction(self, new_dir: Direction) -> None:
        """Remember a turn; applied on the next tick (prevents instant 180)."""
        if new_dir == _OPPOSITE.get(self.direction):
            return
        self._queued_direction = new_dir

    def tick(self) -> None:
        """Advance one step; no-op if already game over."""
        if self.game_over:
            return

        if self._queued_direction is not None:
            self.direction = self._queued_direction
            self._queued_direction = None

        hx, hy = self.snake[-1]
        nx, ny = hx + self.direction.dx, hy + self.direction.dy

        if not (0 <= nx < self.width and 0 <= ny < self.height):
            self.game_over = True
            return

        new_head = (nx, ny)
        if new_head in self.snake:
            self.game_over = True
            return

        ate = new_head == self.food
        self.snake.append(new_head)
        if ate:
            self.score += 1
            self.food = self._random_food(
                self.width,
                self.height,
                frozenset(self.snake),
            )
        else:
            self.snake.popleft()

    def reset(self) -> None:
        """Start a fresh run with the same grid dimensions."""
        fresh = SerpentineModel.new(self.width, self.height)
        self.snake = fresh.snake
        self.direction = fresh.direction
        self.food = fresh.food
        self.score = fresh.score
        self.game_over = fresh.game_over
        self._queued_direction = None

    def render_lines(self) -> list[str]:
        """ASCII rows for the playfield (one char per cell)."""
        occupied = {cell: i for i, cell in enumerate(self.snake)}
        head = self.snake[-1]
        lines: list[str] = []
        for y in range(self.height):
            row: list[str] = []
            for x in range(self.width):
                if (x, y) == self.food:
                    row.append("*")
                elif (x, y) == head:
                    row.append("@")
                elif (x, y) in occupied:
                    row.append("o")
                else:
                    row.append(".")
            lines.append("".join(row))
        return lines
