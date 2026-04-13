"""Shared tests: app wiring and generic registry invariants."""

from __future__ import annotations

from textual.screen import Screen

from terminal_games.app import TerminalGamesApp, run_app
from terminal_games.games.registry import get_games


def test_imports_resolve() -> None:
    assert TerminalGamesApp is not None
    assert run_app is not None
    assert get_games is not None


def test_registry_games_are_well_formed() -> None:
    games = get_games()
    assert len(games) >= 1

    ids: list[str] = []
    for g in games:
        assert g.game_id
        assert g.title
        ids.append(g.game_id)

    assert len(ids) == len(set(ids)), "game_id values must be unique"

    def return_to_menu() -> None:
        pass

    for g in games:
        screen = g.build_screen(return_to_menu)
        assert isinstance(screen, Screen)
