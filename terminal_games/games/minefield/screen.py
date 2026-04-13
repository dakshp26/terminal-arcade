"""Minefield Textual screen: input and view over ``MinefieldModel``."""

from __future__ import annotations

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from terminal_games import theme
from terminal_games.games.minefield.model import MinefieldModel
from terminal_games.games.protocol import ReturnToMenu, TerminalGame

_CELL_STYLES: dict[str, str] = {
    "#": "white",
    "F": theme.GAME_OVER,               # flagged cell
    ".": theme.LABEL,                   # revealed empty
    # numbers 1-8: kept as literals
    "1": "bold bright_blue",
    "2": "bold green",
    "3": "bold bright_red",
    "4": "bold blue",
    "5": "bold red",
    "6": "bold cyan",
    "7": "bold magenta",
    "8": "dim",
    "*": theme.MINEFIELD_DANGER,        # exposed mine
    "!": "bold white on red",           # wrongly flagged cell (highlight)
}


def _mf_field_panel(model: MinefieldModel) -> Panel:
    lines = model.render_lines()
    t = Text()
    for y, row in enumerate(lines):
        if y:
            t.append("\n")
        for x, ch in enumerate(row):
            is_cursor = x == model.cursor_x and y == model.cursor_y
            base = _CELL_STYLES.get(ch, "")
            style = f"{base} reverse".strip() if is_cursor else base
            t.append(ch, style=style)
            t.append(" ")
    return Panel.fit(t, border_style=theme.MINEFIELD_ACCENT)


def _status_text(model: MinefieldModel) -> Text:
    t = Text()
    t.append("Mines: ", style=theme.LABEL)
    t.append(str(model.flags_remaining), style=theme.MINEFIELD_DANGER)
    t.append("  ·  ", style=theme.LABEL)
    if model.game_over:
        if model.won:
            t.append("Field cleared!", style=theme.WIN)
        else:
            t.append("BOOM!", style=theme.MINEFIELD_DANGER)
            t.append(" You hit a mine", style=theme.LABEL)
        t.append(" — press ", style=theme.LABEL)
        t.append("R", style=theme.RESTART_KEY)
        t.append(" to restart", style=theme.LABEL)
    else:
        t.append("arrows move · Space/Enter reveal · F flag · Esc menu", style=theme.LABEL)
    return t


class MinefieldScreen(Screen[None]):
    """Play Minefield; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = MinefieldModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("Minefield", style=theme.MINEFIELD_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_status_text(self._model)), id="mf_status")
            yield Static(Align.center(_mf_field_panel(self._model)), id="mf_field")
            yield Footer()

    def on_mount(self) -> None:
        self._refresh_view()

    def on_key(self, event: events.Key) -> None:
        key = event.key
        moved = False
        if key in ("up", "w", "k"):
            self._model.move_cursor(0, -1)
            moved = True
        elif key in ("down", "s", "j"):
            self._model.move_cursor(0, 1)
            moved = True
        elif key in ("left", "a", "h"):
            self._model.move_cursor(-1, 0)
            moved = True
        elif key in ("right", "d", "l"):
            self._model.move_cursor(1, 0)
            moved = True
        elif key in ("space", "enter") and not self._model.game_over:
            self._model.reveal()
            moved = True
        elif key == "f" and not self._model.game_over:
            self._model.toggle_flag()
            moved = True
        if moved:
            self._refresh_view()

    def action_back(self) -> None:
        self._return_to_menu()

    def action_restart(self) -> None:
        self._model.reset()
        self._refresh_view()

    def _refresh_view(self) -> None:
        self.query_one("#mf_status", Static).update(Align.center(_status_text(self._model)))
        self.query_one("#mf_field", Static).update(Align.center(_mf_field_panel(self._model)))


class MinefieldGameEntry(TerminalGame):
    """Registry entry for Minefield."""

    @property
    def game_id(self) -> str:
        return "minefield"

    @property
    def title(self) -> str:
        return "Minefield"

    @property
    def description(self) -> str:
        return "Uncover a grid hiding 25 mines using numbered clues. Flag the mines without triggering one."

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return MinefieldScreen(return_to_menu)
