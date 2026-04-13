"""Starfall game tests."""

from __future__ import annotations

import random

from textual.screen import Screen

from terminal_games.games.starfall.model import StarfallModel
from terminal_games.games.starfall.screen import (
    StarfallGameEntry,
    StarfallScreen,
)


def test_starfall_game_entry_builds_screen() -> None:
    entry = StarfallGameEntry()
    assert entry.game_id == "starfall"
    assert entry.title

    def return_to_menu() -> None:
        pass

    screen = entry.build_screen(return_to_menu)
    assert isinstance(screen, Screen)
    assert isinstance(screen, StarfallScreen)


def test_starfall_model_ticks_without_crash() -> None:
    random.seed(0)
    model = StarfallModel.new(width=40, height=18)
    assert not model.game_over
    assert model.lives >= 1
    assert model.aliens

    for _ in range(30):
        model.tick()
        model.try_fire()
        if model.game_over:
            break

    assert isinstance(model.score, int)
    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)
