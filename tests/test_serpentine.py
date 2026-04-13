"""Serpentine game tests."""

from __future__ import annotations

import random

from textual.screen import Screen

from terminal_games.games.serpentine.model import Direction, SerpentineModel
from terminal_games.games.serpentine.screen import SerpentineGameEntry, SerpentineScreen

_OPPOSITE: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


def test_serpentine_game_entry_builds_screen() -> None:
    entry = SerpentineGameEntry()
    assert entry.game_id == "serpentine"
    assert entry.title

    def return_to_menu() -> None:
        pass

    screen = entry.build_screen(return_to_menu)
    assert isinstance(screen, Screen)
    assert isinstance(screen, SerpentineScreen)


def test_serpentine_model_ticks_without_crash() -> None:
    random.seed(0)
    model = SerpentineModel.new(width=16, height=8)
    assert not model.game_over
    assert len(model.snake) >= 1

    for _ in range(10):
        model.tick()
        if model.game_over:
            break

    assert isinstance(model.score, int)
    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)


def test_serpentine_queue_direction_ignores_reverse() -> None:
    random.seed(1)
    model = SerpentineModel.new(width=20, height=10)
    initial_dir = model.direction
    model.queue_direction(_OPPOSITE[initial_dir])
    model.tick()
    assert model.direction == initial_dir
