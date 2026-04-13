"""Serpentine Textual screen: input, timer, and view over ``SerpentineModel``."""

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
from terminal_games.games.protocol import ReturnToMenu, TerminalGame
from terminal_games.games.serpentine.model import Direction, SerpentineModel

_TICK_SECONDS = 0.12

_CELL_STYLES: dict[str, str] = {
    ".": theme.LABEL,
    "o": theme.SERPENTINE_ACCENT,   # snake body
    "@": theme.SERPENTINE_TITLE,    # snake head
    "*": theme.SERPENTINE_FOOD,     # food pellet
}


def _serpentine_field_panel(model: SerpentineModel) -> Panel:
    t = Text()
    for y, line in enumerate(model.render_lines()):
        if y:
            t.append("\n")
        for ch in line:
            t.append(ch, style=_CELL_STYLES.get(ch, ""))
    return Panel.fit(t, border_style=theme.SERPENTINE_ACCENT)


def _score_text(model: SerpentineModel) -> Text:
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
        t.append("Esc menu · R restart · arrows or WASD", style=theme.LABEL)
    return t


class SerpentineScreen(Screen[None]):
    """Play Serpentine; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = SerpentineModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("Serpentine", style=theme.SERPENTINE_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_score_text(self._model)), id="score_line")
            yield Static(Align.center(_serpentine_field_panel(self._model)), id="field")
            yield Footer()

    def on_mount(self) -> None:
        self.set_interval(_TICK_SECONDS, self._on_tick)
        self._refresh_view()

    def on_key(self, event: events.Key) -> None:
        if self._model.game_over:
            return
        key = event.key
        direction: Direction | None = None
        if key in ("up", "k"):
            direction = Direction.UP
        elif key in ("down", "j"):
            direction = Direction.DOWN
        elif key in ("left", "h"):
            direction = Direction.LEFT
        elif key in ("right", "l"):
            direction = Direction.RIGHT
        elif key == "w":
            direction = Direction.UP
        elif key == "s":
            direction = Direction.DOWN
        elif key == "a":
            direction = Direction.LEFT
        elif key == "d":
            direction = Direction.RIGHT
        if direction is not None:
            self._model.queue_direction(direction)

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
        score = self.query_one("#score_line", Static)
        field = self.query_one("#field", Static)
        score.update(Align.center(_score_text(self._model)))
        field.update(Align.center(_serpentine_field_panel(self._model)))


class SerpentineGameEntry(TerminalGame):
    """Registry entry for Serpentine."""

    @property
    def game_id(self) -> str:
        return "serpentine"

    @property
    def title(self) -> str:
        return "Serpentine"

    @property
    def description(self) -> str:
        return "Steer a growing snake around the screen to eat food. Avoid hitting walls or your own tail."

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return SerpentineScreen(return_to_menu)
