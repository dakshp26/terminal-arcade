"""AsterAvoid game tests."""

from __future__ import annotations

import random

from textual.screen import Screen

from terminal_games.games.asteravoid.model import AsterAvoidModel
from terminal_games.games.asteravoid.screen import AsterAvoidGameEntry, AsterAvoidScreen


def test_asteravoid_game_entry_builds_screen() -> None:
    entry = AsterAvoidGameEntry()
    assert entry.game_id == "asteravoid"
    assert entry.title

    def return_to_menu() -> None:
        pass

    screen = entry.build_screen(return_to_menu)
    assert isinstance(screen, Screen)
    assert isinstance(screen, AsterAvoidScreen)


def test_asteravoid_model_ticks_without_crash() -> None:
    random.seed(0)
    model = AsterAvoidModel.new(width=40, height=20)
    assert not model.game_over

    for _ in range(50):
        model.tick()
        if model.game_over:
            break

    assert isinstance(model.score, int)
    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)


def test_asteravoid_ship_stays_in_bounds() -> None:
    model = AsterAvoidModel.new(width=20, height=10)
    for _ in range(100):
        model.move_ship(-1)
    assert model.ship_x == 0

    for _ in range(100):
        model.move_ship(1)
    assert model.ship_x == model.width - model.ship_width
