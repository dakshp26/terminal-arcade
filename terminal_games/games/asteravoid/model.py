"""Pure AsterAvoid rules: no Textual or Rich imports."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

_EMPTY = " "
_ASTEROID = "*"
_SHIP_LEFT = "<"
_SHIP_MID = "^"
_SHIP_RIGHT = ">"

_STARTING_MOVE_PERIOD = 8   # ticks between asteroid rows dropping
_STARTING_SPAWN_PERIOD = 15 # ticks between new asteroid spawns
_MAX_ASTEROIDS = 12


@dataclass
class AsterAvoidModel:
    """Asteroid dodger: ``tick()`` drops rocks, scores time survived, speeds up."""

    width: int
    height: int
    ship_x: int
    ship_width: int
    ship_y: int
    asteroids: list[tuple[int, int]]
    score: int
    game_over: bool
    tick_index: int
    _ticks_until_move: int = field(default=_STARTING_MOVE_PERIOD, repr=False)
    _ticks_until_spawn: int = field(default=_STARTING_SPAWN_PERIOD, repr=False)

    @classmethod
    def new(cls, width: int = 40, height: int = 20) -> AsterAvoidModel:
        ship_width = 3
        ship_y = height - 1
        ship_x = (width - ship_width) // 2
        return cls(
            width=width,
            height=height,
            ship_x=ship_x,
            ship_width=ship_width,
            ship_y=ship_y,
            asteroids=[],
            score=0,
            game_over=False,
            tick_index=0,
        )

    def reset(self) -> None:
        fresh = AsterAvoidModel.new(self.width, self.height)
        self.ship_x = fresh.ship_x
        self.asteroids = fresh.asteroids
        self.score = fresh.score
        self.game_over = fresh.game_over
        self.tick_index = fresh.tick_index
        self._ticks_until_move = fresh._ticks_until_move
        self._ticks_until_spawn = fresh._ticks_until_spawn

    def _current_move_period(self) -> int:
        return max(1, _STARTING_MOVE_PERIOD - self.score // 100)

    def _current_spawn_period(self) -> int:
        return max(5, _STARTING_SPAWN_PERIOD - self.score // 50)

    def move_ship(self, delta: int) -> None:
        if self.game_over:
            return
        nx = self.ship_x + delta
        self.ship_x = max(0, min(nx, self.width - self.ship_width))

    def tick(self) -> None:
        if self.game_over:
            return

        self.tick_index += 1
        self.score += 1

        self._ticks_until_move -= 1
        if self._ticks_until_move <= 0:
            self._ticks_until_move = self._current_move_period()
            self._drop_asteroids()

        self._ticks_until_spawn -= 1
        if self._ticks_until_spawn <= 0:
            self._ticks_until_spawn = self._current_spawn_period()
            self._spawn_asteroid()

        self._check_collision()

    def _drop_asteroids(self) -> None:
        self.asteroids = [
            (ax, ay + 1)
            for ax, ay in self.asteroids
            if ay + 1 < self.height
        ]

    def _spawn_asteroid(self) -> None:
        if len(self.asteroids) >= _MAX_ASTEROIDS:
            return
        self.asteroids.append((random.randint(0, self.width - 1), 0))

    def _check_collision(self) -> None:
        ship_cells = frozenset(
            (self.ship_x + i, self.ship_y) for i in range(self.ship_width)
        )
        for ax, ay in self.asteroids:
            if (ax, ay) in ship_cells:
                self.game_over = True
                return

    def render_lines(self) -> list[str]:
        grid: list[list[str]] = [
            [_EMPTY] * self.width for _ in range(self.height)
        ]

        for ax, ay in self.asteroids:
            if 0 <= ay < self.height and 0 <= ax < self.width:
                grid[ay][ax] = _ASTEROID

        for i in range(self.ship_width):
            px = self.ship_x + i
            if 0 <= px < self.width:
                if i == 0:
                    grid[self.ship_y][px] = _SHIP_LEFT
                elif i == self.ship_width // 2:
                    grid[self.ship_y][px] = _SHIP_MID
                else:
                    grid[self.ship_y][px] = _SHIP_RIGHT

        return ["".join(row) for row in grid]
