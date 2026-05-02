"""Floodgate game tests."""

from __future__ import annotations

import random

from textual.screen import Screen

from terminal_games.games.floodgate.model import FloodgateModel
from terminal_games.games.floodgate.screen import FloodgateGameEntry, FloodgateScreen


def test_floodgate_game_entry_builds_screen() -> None:
    entry = FloodgateGameEntry()
    assert entry.game_id == "floodgate"
    assert entry.title

    def return_to_menu() -> None:
        pass

    screen = entry.build_screen(return_to_menu)
    assert isinstance(screen, Screen)
    assert isinstance(screen, FloodgateScreen)


def test_floodgate_model_render_dimensions() -> None:
    random.seed(0)
    model = FloodgateModel.new(width=14, height=14)
    assert not model.game_over
    assert not model.won
    assert model.moves == 0
    assert model.owned[0][0]  # top-left is always owned at start

    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)


def test_floodgate_flood_expands_territory() -> None:
    random.seed(42)
    model = FloodgateModel.new(width=14, height=14)
    initial_owned = model.owned_count

    # Pick any colour different from the current one
    target = (model.current_color + 1) % model.colors
    model.flood(target)

    assert model.moves == 1
    assert model.owned_count >= initial_owned
    assert model.current_color == target


def test_floodgate_same_color_noop() -> None:
    random.seed(7)
    model = FloodgateModel.new(width=14, height=14)
    before_moves = model.moves
    before_owned = model.owned_count

    model.flood(model.current_color)

    assert model.moves == before_moves
    assert model.owned_count == before_owned
