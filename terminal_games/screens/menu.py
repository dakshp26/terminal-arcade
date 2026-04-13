"""Launcher screen: pick a game from the registry."""

from __future__ import annotations

from collections.abc import Sequence

from rich.align import Align
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, OptionList, Static
from textual.widgets.option_list import Option

from terminal_games.games.protocol import TerminalGame
from terminal_games import theme


class MenuScreen(Screen[None]):
    """Shows registered games; selection pushes the game's screen."""

    BINDINGS = [
        Binding("escape,q", "quit", "Quit"),
    ]

    def __init__(self, games: Sequence[TerminalGame]) -> None:
        super().__init__()
        self._games: dict[str, TerminalGame] = {g.game_id: g for g in games}

    _ASCII = (
        "▀█▀ █▀▀ █▀█ █▀▄▀█ █ █▄ █ ▄▀█ █ \n"
        "  █  ██▄ █▀▄ █ ▀ █ █ █ ▀█ █▀█ █▄\n"
        "\n"
        "▄▀█ █▀█ █▀▀ ▄▀█ █▀▄ █▀▀\n"
        "█▀█ █▀▄ █▄▄ █▀█ █▄▀ ██▄"
    )

    def compose(self) -> ComposeResult:
        with Vertical():
            art = Text(self._ASCII, style=theme.MENU_TITLE, justify="center")
            art.append("\n\nSelect with ↑↓ and Enter · Esc or Q to quit", style=theme.LABEL)
            art.append("\n★ github.com/dakshp26/terminal-arcade", style=theme.LABEL)
            header = Align.center(
                Panel.fit(
                    art,
                    border_style=theme.MENU_ACCENT,
                )
            )
            yield Static(header, id="title")
            yield Static(Rule(style=f"dim {theme.MENU_ACCENT}"), id="menu_rule")
            options = [
                Option(self._rich_prompt(g), id=g.game_id) for g in self._games.values()
            ]
            yield OptionList(*options, id="game_list")
            yield Footer()

    @staticmethod
    def _rich_prompt(game: TerminalGame) -> Text:
        t = Text()
        t.append(game.title, style=theme.MENU_GAME_TITLE)
        if game.description:
            t.append("\n")
            t.append(game.description, style=f"{theme.LABEL} italic")
        return t

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        game_id = event.option_id
        if game_id is None or game_id not in self._games:
            return
        game = self._games[game_id]

        def return_to_menu() -> None:
            self.app.pop_screen()

        self.app.push_screen(game.build_screen(return_to_menu))

    def action_quit(self) -> None:
        self.app.exit()
