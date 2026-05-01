"""Pure Echo Chamber rules: no Textual or Rich imports.

Navigate a dark cave as a bat. Press Space to emit a sonar pulse that
illuminates nearby cells. The glow fades from edges inward each tick.
Reach the exit (>) to advance levels; avoid enemy bats (*) or lose a life.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

_EMPTY = " "
_WALL = "#"
_FLOOR = "."
_PLAYER = "@"
_EXIT = ">"
_BAT = "*"

_PULSE_RADIUS = 8
_PULSE_MAX_INTENSITY = 4
_BAT_MOVE_INTERVAL = 4  # ticks between bat steps


def _generate_cave(width: int, height: int) -> list[list[bool]]:
    """Recursive-backtracker perfect maze. True = wall, False = floor."""
    cave = [[True] * width for _ in range(height)]
    visited = [[False] * width for _ in range(height)]

    def carve(x: int, y: int) -> None:
        cave[y][x] = False
        visited[y][x] = True
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and not visited[ny][nx]:
                cave[y + dy // 2][x + dx // 2] = False
                carve(nx, ny)

    carve(1, 1)
    return cave


def _nearest_odd(n: int) -> int:
    return n if n % 2 == 1 else n - 1


def _place_bats(
    cave: list[list[bool]],
    width: int,
    height: int,
    count: int,
    exclude: set[tuple[int, int]],
    min_dist: int = 5,
) -> list[tuple[int, int]]:
    """Place bats on floor cells at least min_dist (Manhattan) from all excluded positions."""
    candidates = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if not cave[y][x]
        and (x, y) not in exclude
        and all(abs(x - ex) + abs(y - ey) >= min_dist for ex, ey in exclude)
    ]
    if not candidates:
        candidates = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if not cave[y][x] and (x, y) not in exclude
        ]
    random.shuffle(candidates)
    return candidates[:count]


@dataclass
class EchoChamberModel:
    """Sonar bat navigation: pulse to see, navigate to the exit."""

    width: int
    height: int
    cave: list[list[bool]]
    player_x: int
    player_y: int
    exit_x: int
    exit_y: int
    bats: list[tuple[int, int]]
    echo_grid: list[list[int]]
    score: int
    lives: int
    level: int
    game_over: bool
    _bat_tick: int = field(default=0, repr=False)

    @classmethod
    def new(cls, width: int = 30, height: int = 15) -> EchoChamberModel:
        cave = _generate_cave(width, height)
        player_x, player_y = 1, 1
        exit_x = _nearest_odd(width - 2)
        exit_y = _nearest_odd(height - 2)
        cave[exit_y][exit_x] = False
        bats = _place_bats(
            cave, width, height,
            count=2,
            exclude={(player_x, player_y), (exit_x, exit_y)},
        )
        echo_grid = [[0] * width for _ in range(height)]
        model = cls(
            width=width,
            height=height,
            cave=cave,
            player_x=player_x,
            player_y=player_y,
            exit_x=exit_x,
            exit_y=exit_y,
            bats=bats,
            echo_grid=echo_grid,
            score=0,
            lives=3,
            level=1,
            game_over=False,
            _bat_tick=0,
        )
        model.pulse()
        return model

    def reset(self) -> None:
        fresh = EchoChamberModel.new(self.width, self.height)
        self.cave = fresh.cave
        self.player_x = fresh.player_x
        self.player_y = fresh.player_y
        self.exit_x = fresh.exit_x
        self.exit_y = fresh.exit_y
        self.bats = fresh.bats
        self.echo_grid = fresh.echo_grid
        self.score = fresh.score
        self.lives = fresh.lives
        self.level = fresh.level
        self.game_over = fresh.game_over
        self._bat_tick = fresh._bat_tick

    def pulse(self) -> None:
        """Emit a sonar pulse from the player's position."""
        if self.game_over:
            return
        px, py = self.player_x, self.player_y
        for dy in range(-_PULSE_RADIUS, _PULSE_RADIUS + 1):
            for dx in range(-_PULSE_RADIUS, _PULSE_RADIUS + 1):
                x, y = px + dx, py + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    dist = max(abs(dx), abs(dy))
                    # Intensity decreases linearly from centre to edge
                    intensity = max(
                        0,
                        _PULSE_MAX_INTENSITY
                        - dist * _PULSE_MAX_INTENSITY // _PULSE_RADIUS,
                    )
                    if intensity > 0:
                        self.echo_grid[y][x] = max(self.echo_grid[y][x], intensity)

    def move(self, dx: int, dy: int) -> None:
        """Attempt to move player by (dx, dy). Walls block silently."""
        if self.game_over:
            return
        nx, ny = self.player_x + dx, self.player_y + dy
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return
        if self.cave[ny][nx]:
            return
        self.player_x, self.player_y = nx, ny
        self._check_bat_collision()
        if not self.game_over:
            self._check_exit()

    def tick(self) -> None:
        """Decay echo intensities and periodically move bats."""
        if self.game_over:
            return
        for y in range(self.height):
            for x in range(self.width):
                if self.echo_grid[y][x] > 0:
                    self.echo_grid[y][x] -= 1
        self._bat_tick += 1
        if self._bat_tick >= _BAT_MOVE_INTERVAL:
            self._bat_tick = 0
            self._move_bats()
            self._check_bat_collision()

    def _move_bats(self) -> None:
        occupied = set(self.bats)
        new_bats: list[tuple[int, int]] = []
        for bx, by in self.bats:
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(dirs)
            moved = False
            for ddx, ddy in dirs:
                nx, ny = bx + ddx, by + ddy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not self.cave[ny][nx]
                    and (nx, ny) not in occupied
                ):
                    occupied.discard((bx, by))
                    occupied.add((nx, ny))
                    new_bats.append((nx, ny))
                    moved = True
                    break
            if not moved:
                new_bats.append((bx, by))
        self.bats = new_bats

    def _check_bat_collision(self) -> None:
        pos = (self.player_x, self.player_y)
        if pos in self.bats:
            self.bats = [b for b in self.bats if b != pos]
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True

    def _check_exit(self) -> None:
        if self.player_x == self.exit_x and self.player_y == self.exit_y:
            self.score += self.level * 100
            self._next_level()

    def _next_level(self) -> None:
        self.level += 1
        cave = _generate_cave(self.width, self.height)
        exit_x = _nearest_odd(self.width - 2)
        exit_y = _nearest_odd(self.height - 2)
        cave[exit_y][exit_x] = False
        bat_count = min(self.level + 1, 8)
        bats = _place_bats(
            cave, self.width, self.height,
            count=bat_count,
            exclude={(1, 1), (exit_x, exit_y)},
        )
        self.cave = cave
        self.player_x, self.player_y = 1, 1
        self.exit_x, self.exit_y = exit_x, exit_y
        self.bats = bats
        self.echo_grid = [[0] * self.width for _ in range(self.height)]
        self._bat_tick = 0
        self.pulse()

    def render_lines(self) -> list[str]:
        """ASCII rows for the playfield (one char per cell)."""
        bat_positions = set(self.bats)
        grid: list[list[str]] = []
        for y in range(self.height):
            row: list[str] = []
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    row.append(_PLAYER)
                elif self.echo_grid[y][x] > 0:
                    if self.cave[y][x]:
                        row.append(_WALL)
                    elif x == self.exit_x and y == self.exit_y:
                        row.append(_EXIT)
                    elif (x, y) in bat_positions:
                        row.append(_BAT)
                    else:
                        row.append(_FLOOR)
                else:
                    row.append(_EMPTY)
            grid.append(row)
        return ["".join(row) for row in grid]
