"""Abstract game contract for the launcher (dependency inversion)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias

from textual.screen import Screen

ReturnToMenu: TypeAlias = Callable[[], None]
"""Callback that returns the user to the main menu (e.g. ``app.pop_screen``)."""


class TerminalGame(ABC):
    """Registerable game: metadata plus a factory for its play screen."""

    @property
    @abstractmethod
    def game_id(self) -> str: ...

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    def description(self) -> str:
        return ""

    @abstractmethod
    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen: ...
