"""Echo Chamber Textual screen: input, timer, and view over ``EchoChamberModel``."""

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
from terminal_games.games.echo_chamber.model import EchoChamberModel
from terminal_games.games.protocol import ReturnToMenu, TerminalGame

_TICK_SECONDS = 0.12

_WALL_STYLES = {
    4: theme.ECHO_WALL_4,
    3: theme.ECHO_WALL_3,
    2: theme.ECHO_WALL_2,
    1: theme.ECHO_WALL_1,
}
_FLOOR_STYLES = {
    4: theme.ECHO_FLOOR_4,
    3: theme.ECHO_FLOOR_3,
    2: theme.ECHO_FLOOR_2,
    1: theme.ECHO_FLOOR_1,
}


def _cell_style(ch: str, intensity: int) -> str:
    if ch == "@":
        return theme.ECHO_TITLE
    if ch == "#":
        return _WALL_STYLES.get(intensity, "")
    if ch == ".":
        return _FLOOR_STYLES.get(intensity, "")
    if ch == ">":
        return theme.ECHO_EXIT
    if ch == "*":
        return theme.ECHO_BAT
    return ""


def _field_panel(model: EchoChamberModel) -> Panel:
    t = Text()
    lines = model.render_lines()
    for y, line in enumerate(lines):
        if y:
            t.append("\n")
        for x, ch in enumerate(line):
            intensity = model.echo_grid[y][x]
            t.append(ch, style=_cell_style(ch, intensity))
    return Panel.fit(t, border_style=theme.ECHO_ACCENT)


def _hud_text(model: EchoChamberModel) -> Text:
    t = Text()
    t.append("Score: ", style=theme.LABEL)
    t.append(str(model.score), style=theme.SCORE_VALUE)
    t.append("  ·  Lives: ", style=theme.LABEL)
    t.append(str(model.lives), style=theme.LIVES_VALUE)
    t.append("  ·  Level: ", style=theme.LABEL)
    t.append(str(model.level), style=theme.WAVE_VALUE)
    t.append("  ·  ", style=theme.LABEL)
    if model.game_over:
        t.append("GAME OVER", style=theme.GAME_OVER)
        t.append(" — press ", style=theme.LABEL)
        t.append("R", style=theme.RESTART_KEY)
        t.append(" to restart", style=theme.LABEL)
    else:
        t.append("Space pulse · arrows move · R restart · Esc menu", style=theme.LABEL)
    return t


class EchoChamberScreen(Screen[None]):
    """Echo Chamber; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
        Binding("space", "pulse", "Pulse"),
        Binding("up", "move_up", "Up"),
        Binding("down", "move_down", "Down"),
        Binding("left", "move_left", "Left"),
        Binding("right", "move_right", "Right"),
        Binding("w", "move_up", "", show=False),
        Binding("s", "move_down", "", show=False),
        Binding("a", "move_left", "", show=False),
        Binding("d", "move_right", "", show=False),
        Binding("k", "move_up", "", show=False),
        Binding("j", "move_down", "", show=False),
        Binding("h", "move_left", "", show=False),
        Binding("l", "move_right", "", show=False),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = EchoChamberModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("Echo Chamber", style=theme.ECHO_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_hud_text(self._model)), id="ec_status")
            yield Static(Align.center(_field_panel(self._model)), id="ec_field")
            yield Footer()

    def on_mount(self) -> None:
        self.set_interval(_TICK_SECONDS, self._on_tick)
        self._refresh_view()

    def _on_tick(self) -> None:
        if self._model.game_over:
            return
        self._model.tick()
        self._refresh_view()

    def action_pulse(self) -> None:
        if not self._model.game_over:
            self._model.pulse()
            self._refresh_view()

    def action_move_up(self) -> None:
        if not self._model.game_over:
            self._model.move(0, -1)
            self._refresh_view()

    def action_move_down(self) -> None:
        if not self._model.game_over:
            self._model.move(0, 1)
            self._refresh_view()

    def action_move_left(self) -> None:
        if not self._model.game_over:
            self._model.move(-1, 0)
            self._refresh_view()

    def action_move_right(self) -> None:
        if not self._model.game_over:
            self._model.move(1, 0)
            self._refresh_view()

    def action_back(self) -> None:
        self._return_to_menu()

    def action_restart(self) -> None:
        self._model.reset()
        self._refresh_view()

    def _refresh_view(self) -> None:
        self.query_one("#ec_status", Static).update(Align.center(_hud_text(self._model)))
        self.query_one("#ec_field", Static).update(Align.center(_field_panel(self._model)))


class EchoChamberGameEntry(TerminalGame):
    """Registry entry for Echo Chamber."""

    @property
    def game_id(self) -> str:
        return "echo_chamber"

    @property
    def title(self) -> str:
        return "Echo Chamber"

    @property
    def description(self) -> str:
        return "You are a bat in an unlit cave maze. Space emits sonar—cells near you light up, then the bright ring contracts each tick. Step on the exit to advance; enemy bats remove a life on contact."

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return EchoChamberScreen(return_to_menu)
