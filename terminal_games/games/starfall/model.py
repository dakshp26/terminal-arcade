"""Pure Starfall rules: no Textual or Rich imports."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

_EMPTY = " "
_ALIEN = "M"
_PLAYER_SIDE = "="
_PLAYER_MID = "^"
_BULLET_UP = "|"
_BULLET_DOWN = ":"

# Lower period = faster alien formation. Higher = more alien shots per tick on average.
_STARTING_ALIEN_MOVE_PERIOD = 8
_ALIEN_SHOOT_CHANCE = 0.065
# Player bullet cells moved upward per tick (faster = shorter time until next shot).
_PLAYER_BULLET_CELLS_PER_TICK = 2


def _formation_cells(
    width: int,
    rows: int,
    cols: int,
    top_row: int,
    h_spacing: int,
) -> set[tuple[int, int]]:
    """Place a rectangular alien grid, horizontally centered."""
    span = cols + (cols - 1) * (h_spacing - 1)
    start_x = max(0, (width - span) // 2)
    cells: set[tuple[int, int]] = set()
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * h_spacing
            cells.add((x, top_row + r))
    return cells


@dataclass
class StarfallModel:
    """ASCII grid shooter: ``tick()`` advances bullets, aliens on a schedule, and shots."""

    width: int
    height: int
    aliens: set[tuple[int, int]]
    alien_dx: int
    player_x: int
    player_width: int
    player_y: int
    player_bullets: list[tuple[int, int]]
    alien_bullets: list[tuple[int, int]]
    score: int
    lives: int
    game_over: bool
    wave: int
    tick_index: int
    alien_move_period: int
    _ticks_until_alien_step: int = field(default=0, repr=False)

    @classmethod
    def new(
        cls,
        width: int = 52,
        height: int = 22,
        alien_rows: int = 4,
        alien_cols: int = 9,
    ) -> StarfallModel:
        player_width = 3
        player_y = height - 1
        player_x = max(0, (width - player_width) // 2)
        aliens = _formation_cells(
            width, alien_rows, alien_cols, top_row=1, h_spacing=2
        )
        return cls(
            width=width,
            height=height,
            aliens=aliens,
            alien_dx=1,
            player_x=player_x,
            player_width=player_width,
            player_y=player_y,
            player_bullets=[],
            alien_bullets=[],
            score=0,
            lives=3,
            game_over=False,
            wave=1,
            tick_index=0,
            alien_move_period=_STARTING_ALIEN_MOVE_PERIOD,
            _ticks_until_alien_step=_STARTING_ALIEN_MOVE_PERIOD,
        )

    def reset(self) -> None:
        """New run with same dimensions."""
        fresh = StarfallModel.new(self.width, self.height)
        self.aliens = fresh.aliens
        self.alien_dx = fresh.alien_dx
        self.player_x = fresh.player_x
        self.player_bullets = fresh.player_bullets
        self.alien_bullets = fresh.alien_bullets
        self.score = fresh.score
        self.lives = fresh.lives
        self.game_over = fresh.game_over
        self.wave = fresh.wave
        self.tick_index = fresh.tick_index
        self.alien_move_period = fresh.alien_move_period
        self._ticks_until_alien_step = fresh._ticks_until_alien_step

    def try_fire(self) -> None:
        """Fire one upward bullet if none is in flight and game is active."""
        if self.game_over or self.lives <= 0:
            return
        if self.player_bullets:
            return
        bx = self.player_x + self.player_width // 2
        by = self.player_y - 1
        if by >= 0:
            self.player_bullets.append((bx, by))

    def move_player(self, delta: int) -> None:
        """Move ship horizontally by delta cells (clamped)."""
        if self.game_over:
            return
        nx = self.player_x + delta
        nx = max(0, min(nx, self.width - self.player_width))
        self.player_x = nx

    def tick(self) -> None:
        """Advance simulation by one frame."""
        if self.game_over:
            return

        self.tick_index += 1

        # Player bullets up (multi-step per tick); stop on first alien or top edge
        next_pb: list[tuple[int, int]] = []
        hit_cells: set[tuple[int, int]] = set()
        for bx, by in self.player_bullets:
            y = by
            stopped = False
            for _ in range(_PLAYER_BULLET_CELLS_PER_TICK):
                y -= 1
                if y < 0:
                    stopped = True
                    break
                if (bx, y) in self.aliens:
                    hit_cells.add((bx, y))
                    self.score += 10
                    stopped = True
                    break
            if not stopped:
                next_pb.append((bx, y))
        self.player_bullets = next_pb
        self.aliens -= hit_cells

        # Alien bullets down
        next_ab: list[tuple[int, int]] = []
        for bx, by in self.alien_bullets:
            ny = by + 1
            if ny >= self.height:
                continue
            next_ab.append((bx, ny))
        self.alien_bullets = next_ab

        # Alien bullet vs player (one hit processed per tick)
        player_cells = {
            (self.player_x + i, self.player_y) for i in range(self.player_width)
        }
        took_hit = False
        new_ab: list[tuple[int, int]] = []
        for bx, by in self.alien_bullets:
            if not took_hit and (bx, by) in player_cells:
                self.lives -= 1
                took_hit = True
                if self.lives <= 0:
                    self.game_over = True
                continue
            new_ab.append((bx, by))
        self.alien_bullets = new_ab

        if self.game_over:
            return

        # Alien march
        self._ticks_until_alien_step -= 1
        if self._ticks_until_alien_step <= 0:
            self._ticks_until_alien_step = self.alien_move_period
            self._step_aliens()

        if self.game_over:
            return

        if not self.aliens:
            self._next_wave()
            return

        # Random alien shot from bottom of a random column
        if self.aliens and random.random() < _ALIEN_SHOOT_CHANCE:
            self._alien_shoot()

        self._check_alien_landed()

    def _step_aliens(self) -> None:
        dx = self.alien_dx
        hit_wall = False
        for ax, _ay in self.aliens:
            nx = ax + dx
            if nx < 0 or nx >= self.width:
                hit_wall = True
                break
        if hit_wall:
            new_aliens: set[tuple[int, int]] = set()
            for ax, ay in self.aliens:
                new_aliens.add((ax, ay + 1))
            self.aliens = new_aliens
            self.alien_dx = -dx
        else:
            self.aliens = {(ax + dx, ay) for ax, ay in self.aliens}

    def _next_wave(self) -> None:
        self.wave += 1
        self.alien_move_period = max(4, self.alien_move_period - 1)
        self._ticks_until_alien_step = self.alien_move_period
        self.aliens = _formation_cells(
            self.width, rows=4, cols=9, top_row=1, h_spacing=2
        )
        self.alien_dx = 1
        self.player_bullets.clear()
        self.alien_bullets.clear()

    def _alien_shoot(self) -> None:
        by_col: dict[int, list[tuple[int, int]]] = {}
        for ax, ay in self.aliens:
            by_col.setdefault(ax, []).append((ax, ay))
        if not by_col:
            return
        col_x = random.choice(list(by_col.keys()))
        # Lowest alien in column (max y)
        ax, ay = max(by_col[col_x], key=lambda p: p[1])
        ny = ay + 1
        if ny < self.height:
            self.alien_bullets.append((ax, ny))

    def _check_alien_landed(self) -> None:
        for _ax, ay in self.aliens:
            if ay >= self.player_y:
                self.game_over = True
                return

    def render_lines(self) -> list[str]:
        """ASCII rows for the playfield (one char per cell)."""
        grid: list[list[str]] = [
            [_EMPTY for _ in range(self.width)] for _ in range(self.height)
        ]

        for ax, ay in self.aliens:
            if 0 <= ay < self.height and 0 <= ax < self.width:
                grid[ay][ax] = _ALIEN

        for i in range(self.player_width):
            px = self.player_x + i
            if 0 <= px < self.width:
                ch = _PLAYER_MID if i == self.player_width // 2 else _PLAYER_SIDE
                grid[self.player_y][px] = ch

        for bx, by in self.player_bullets:
            if 0 <= by < self.height and 0 <= bx < self.width:
                if grid[by][bx] == _EMPTY:
                    grid[by][bx] = _BULLET_UP

        for bx, by in self.alien_bullets:
            if 0 <= by < self.height and 0 <= bx < self.width:
                grid[by][bx] = _BULLET_DOWN

        return ["".join(row) for row in grid]
