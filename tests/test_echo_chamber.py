"""Echo Chamber game tests."""

from __future__ import annotations

import random

from textual.screen import Screen

from terminal_games.games.echo_chamber.model import EchoChamberModel
from terminal_games.games.echo_chamber.screen import EchoChamberGameEntry, EchoChamberScreen


def test_echo_chamber_game_entry_builds_screen() -> None:
    entry = EchoChamberGameEntry()
    assert entry.game_id == "echo_chamber"
    assert entry.title

    def return_to_menu() -> None:
        pass

    screen = entry.build_screen(return_to_menu)
    assert isinstance(screen, Screen)
    assert isinstance(screen, EchoChamberScreen)


def test_echo_chamber_model_ticks_without_crash() -> None:
    random.seed(0)
    model = EchoChamberModel.new(width=30, height=15)
    assert not model.game_over
    assert model.lives == 3
    assert model.level == 1

    for _ in range(50):
        model.tick()
        if model.game_over:
            break

    assert isinstance(model.score, int)
    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)


def test_echo_chamber_pulse_illuminates_nearby_cells() -> None:
    random.seed(1)
    model = EchoChamberModel.new(width=30, height=15)
    # Reset echo grid then pulse from a known position
    model.echo_grid = [[0] * model.width for _ in range(model.height)]
    model.player_x, model.player_y = 15, 7
    model.pulse()

    # Player cell and immediate neighbours must be illuminated
    assert model.echo_grid[7][15] > 0
    assert model.echo_grid[6][15] > 0
    assert model.echo_grid[7][14] > 0

    # Cells at max radius should have lower or zero intensity than centre
    assert model.echo_grid[7][15] >= model.echo_grid[7][14]


def test_echo_chamber_wall_blocks_movement() -> None:
    random.seed(2)
    model = EchoChamberModel.new(width=30, height=15)
    # Top-left corner is always a wall (row 0 is wall in maze)
    model.player_x, model.player_y = 1, 1
    # Moving into the outer wall (y=0) should be blocked
    model.move(0, -1)
    assert model.player_y == 1  # unchanged: either hit wall or maze edge

    # Moving into column 0 (always a wall) should be blocked
    model.player_x, model.player_y = 1, 1
    model.move(-1, 0)
    assert model.player_x == 1
