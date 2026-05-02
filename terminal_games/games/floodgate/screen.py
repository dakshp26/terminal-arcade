"""Floodgate Textual screen: input and view over ``FloodgateModel``."""

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
from terminal_games.games.floodgate.model import FloodgateModel
from terminal_games.games.protocol import ReturnToMenu, TerminalGame

_BLOCK = "█"   # owned cell

_COLORS_BRIGHT = [
    theme.FLOODGATE_0,
    theme.FLOODGATE_1,
    theme.FLOODGATE_2,
    theme.FLOODGATE_3,
    theme.FLOODGATE_4,
    theme.FLOODGATE_5,
]

_COLORS_DIM = [
    theme.FLOODGATE_0_DIM,
    theme.FLOODGATE_1_DIM,
    theme.FLOODGATE_2_DIM,
    theme.FLOODGATE_3_DIM,
    theme.FLOODGATE_4_DIM,
    theme.FLOODGATE_5_DIM,
]


def _fg_field_panel(model: FloodgateModel) -> Panel:
    t = Text()
    for y, line in enumerate(model.render_lines()):
        if y:
            t.append("\n")
        for ch in line:
            if ch.isupper():
                idx = ord(ch) - 65
                t.append(_BLOCK, style=_COLORS_BRIGHT[idx])
            else:
                idx = ord(ch) - 97
                t.append(str(idx + 1), style=_COLORS_DIM[idx])
    return Panel.fit(t, border_style=theme.FLOODGATE_ACCENT)


def _hud_text(model: FloodgateModel) -> Text:
    t = Text()
    t.append("Moves: ", style=theme.LABEL)
    t.append(str(model.moves), style=theme.SCORE_VALUE)
    t.append(f"/{model.max_moves}", style=theme.LABEL)
    t.append("   Covered: ", style=theme.LABEL)
    t.append(str(model.owned_count), style=theme.SCORE_VALUE)
    t.append(f"/{model.total_cells}   ", style=theme.LABEL)

    for i in range(model.colors):
        cs = _COLORS_BRIGHT[i]
        t.append(_BLOCK, style=cs)
        if i == model.current_color:
            t.append(str(i + 1), style="bold reverse")
        else:
            t.append(str(i + 1), style=theme.LABEL)
        t.append(" ")

    t.append("  ", style=theme.LABEL)
    if model.game_over:
        if model.won:
            t.append("Flooded!", style=theme.WIN)
            t.append(f" in {model.moves} moves", style=theme.LABEL)
        else:
            t.append("Out of moves!", style=theme.GAME_OVER)
        t.append(" — press ", style=theme.LABEL)
        t.append("R", style=theme.RESTART_KEY)
        t.append(" to restart", style=theme.LABEL)
    else:
        t.append("1-6 to flood · Esc menu", style=theme.LABEL)
    return t


class FloodgateScreen(Screen[None]):
    """Play Floodgate; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = FloodgateModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("Floodgate", style=theme.FLOODGATE_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_hud_text(self._model)), id="fg_status")
            yield Static(Align.center(_fg_field_panel(self._model)), id="fg_field")
            yield Footer()

    def on_mount(self) -> None:
        self._refresh_view()

    def on_key(self, event: events.Key) -> None:
        if self._model.game_over:
            return
        if event.key in ("1", "2", "3", "4", "5", "6"):
            self._model.flood(int(event.key) - 1)
            self._refresh_view()

    def action_back(self) -> None:
        self._return_to_menu()

    def action_restart(self) -> None:
        self._model.reset()
        self._refresh_view()

    def _refresh_view(self) -> None:
        self.query_one("#fg_status", Static).update(Align.center(_hud_text(self._model)))
        self.query_one("#fg_field", Static).update(Align.center(_fg_field_panel(self._model)))


class FloodgateGameEntry(TerminalGame):
    """Registry entry for Floodgate."""

    @property
    def game_id(self) -> str:
        return "floodgate"

    @property
    def title(self) -> str:
        return "Floodgate"

    @property
    def description(self) -> str:
        return (
            "Flood-fill from the top-left: each move picks a colour; your region updates and "
            "absorbs every touching cell of that colour. Paint the whole grid within 30 moves."
        )

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return FloodgateScreen(return_to_menu)
