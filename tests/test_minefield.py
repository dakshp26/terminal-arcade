"""Minefield game tests."""

from __future__ import annotations

import random

from textual.screen import Screen

from terminal_games.games.minefield.model import MinefieldModel
from terminal_games.games.minefield.screen import MinefieldGameEntry, MinefieldScreen


def test_minefield_game_entry_builds_screen() -> None:
    entry = MinefieldGameEntry()
    assert entry.game_id == "minefield"
    assert entry.title

    def return_to_menu() -> None:
        pass

    screen = entry.build_screen(return_to_menu)
    assert isinstance(screen, Screen)
    assert isinstance(screen, MinefieldScreen)


def test_minefield_model_initial_render() -> None:
    random.seed(0)
    model = MinefieldModel.new(width=16, height=10, mines=25)
    assert not model.game_over
    assert not model.won
    assert not model.started
    assert model.flags_remaining == 25
    assert model.revealed_count == 0

    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)
    assert all(ch == "#" for row in lines for ch in row)


def test_minefield_first_reveal_is_safe() -> None:
    random.seed(42)
    model = MinefieldModel.new(width=16, height=10, mines=25)
    model.cursor_x = 8
    model.cursor_y = 5
    model.reveal()

    assert model.started
    assert not model.game_over  # first click is always safe
    assert model.revealed_count > 0

    lines = model.render_lines()
    assert len(lines) == model.height
    assert all(len(row) == model.width for row in lines)
