"""AsterAvoid Textual screen: input, timer, and view over ``AsterAvoidModel``."""

from __future__ import annotations

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from terminal_games import theme
from terminal_games.games.asteravoid.model import AsterAvoidModel
from terminal_games.games.protocol import ReturnToMenu, TerminalGame

_TICK_SECONDS = 0.09

_CELL_STYLES: dict[str, str] = {
    " ": "",
    "*": theme.ASTERAVOID_ASTEROID,
    "<": theme.ASTERAVOID_SHIP,
    "^": theme.ASTERAVOID_SHIP,
    ">": theme.ASTERAVOID_SHIP,
}


def _field_panel(model: AsterAvoidModel) -> Panel:
    t = Text()
    for y, line in enumerate(model.render_lines()):
        if y:
            t.append("\n")
        for ch in line:
            t.append(ch, style=_CELL_STYLES.get(ch, ""))
    return Panel.fit(t, border_style=theme.ASTERAVOID_ACCENT)


def _hud_text(model: AsterAvoidModel) -> Text:
    t = Text()
    t.append("Score: ", style=theme.LABEL)
    t.append(str(model.score), style=theme.SCORE_VALUE)
    t.append("  ·  ", style=theme.LABEL)
    if model.game_over:
        t.append("GAME OVER", style=theme.GAME_OVER)
        t.append(" — press ", style=theme.LABEL)
        t.append("R", style=theme.RESTART_KEY)
        t.append(" to restart", style=theme.LABEL)
    else:
        t.append("Dodge the asteroids! ← → to move", style=theme.LABEL)
    return t


class AsterAvoidScreen(Screen[None]):
    """AsterAvoid; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
        Binding("left", "left", "Left"),
        Binding("right", "right", "Right"),
        Binding("a", "left", "", show=False),
        Binding("d", "right", "", show=False),
        Binding("h", "left", "", show=False),
        Binding("l", "right", "", show=False),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = AsterAvoidModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("AsterAvoid", style=theme.ASTERAVOID_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_hud_text(self._model)), id="av_status")
            yield Static(Align.center(_field_panel(self._model)), id="av_field")
            yield Footer()

    def on_mount(self) -> None:
        self.set_interval(_TICK_SECONDS, self._on_tick)
        self._refresh_view()

    def action_left(self) -> None:
        if not self._model.game_over:
            self._model.move_ship(-1)
            self._refresh_view()

    def action_right(self) -> None:
        if not self._model.game_over:
            self._model.move_ship(1)
            self._refresh_view()

    def action_back(self) -> None:
        self._return_to_menu()

    def action_restart(self) -> None:
        self._model.reset()
        self._refresh_view()

    def _on_tick(self) -> None:
        if self._model.game_over:
            return
        self._model.tick()
        self._refresh_view()

    def _refresh_view(self) -> None:
        self.query_one("#av_status", Static).update(Align.center(_hud_text(self._model)))
        self.query_one("#av_field", Static).update(Align.center(_field_panel(self._model)))


class AsterAvoidGameEntry(TerminalGame):
    """Registry entry for AsterAvoid."""

    @property
    def game_id(self) -> str:
        return "asteravoid"

    @property
    def title(self) -> str:
        return "AsterAvoid"

    @property
    def description(self) -> str:
        return "Pilot a spacecraft across the bottom and dodge a relentless barrage of accelerating asteroids falling from above."

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return AsterAvoidScreen(return_to_menu)
