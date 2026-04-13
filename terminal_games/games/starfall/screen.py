"""Starfall Textual screen: input, timer, and view over ``StarfallModel``."""

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
from terminal_games.games.protocol import ReturnToMenu, TerminalGame
from terminal_games.games.starfall.model import StarfallModel

_TICK_SECONDS = 0.09

_CELL_STYLES: dict[str, str] = {
    " ": "",
    "M": theme.STARFALL_TITLE,      # alien
    "=": theme.STARFALL_SHIP_BODY,  # player ship wings
    "^": theme.STARFALL_SHIP_NOSE,  # player ship centre
    "|": theme.STARFALL_BULLET_UP,  # player bullet
    ":": theme.GAME_OVER,           # alien bullet
}


def _field_panel(model: StarfallModel) -> Panel:
    t = Text()
    for y, line in enumerate(model.render_lines()):
        if y:
            t.append("\n")
        for ch in line:
            t.append(ch, style=_CELL_STYLES.get(ch, ""))
    return Panel.fit(t, border_style=theme.STARFALL_ACCENT)


def _hud_text(model: StarfallModel) -> Text:
    t = Text()
    t.append("Score: ", style=theme.LABEL)
    t.append(str(model.score), style=theme.SCORE_VALUE)
    t.append("  ·  Lives: ", style=theme.LABEL)
    t.append(str(model.lives), style=theme.LIVES_VALUE)
    t.append("  ·  Wave: ", style=theme.LABEL)
    t.append(str(model.wave), style=theme.WAVE_VALUE)
    t.append("  ·  ", style=theme.LABEL)
    if model.game_over:
        t.append("GAME OVER", style=theme.GAME_OVER)
        t.append(" — press ", style=theme.LABEL)
        t.append("R", style=theme.RESTART_KEY)
        t.append(" to restart", style=theme.LABEL)
    else:
        t.append("Esc menu · ← → move · Space fire · R restart", style=theme.LABEL)
    return t


class StarfallScreen(Screen[None]):
    """Starfall; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
        Binding("left", "left", "Left"),
        Binding("right", "right", "Right"),
        Binding("a", "left", "", show=False),
        Binding("d", "right", "", show=False),
        Binding("h", "left", "", show=False),
        Binding("l", "right", "", show=False),
        Binding("space", "fire", "Fire"),
        Binding("up", "fire", "", show=False),
        Binding("w", "fire", "", show=False),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = StarfallModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("Starfall", style=theme.STARFALL_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_hud_text(self._model)), id="sf_score_line")
            yield Static(Align.center(_field_panel(self._model)), id="sf_field")
            yield Footer()

    def on_mount(self) -> None:
        self.set_interval(_TICK_SECONDS, self._on_tick)
        self._refresh_view()

    def action_left(self) -> None:
        if not self._model.game_over:
            self._model.move_player(-1)
            self._refresh_view()

    def action_right(self) -> None:
        if not self._model.game_over:
            self._model.move_player(1)
            self._refresh_view()

    def action_fire(self) -> None:
        if not self._model.game_over:
            self._model.try_fire()
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
        score = self.query_one("#sf_score_line", Static)
        field = self.query_one("#sf_field", Static)
        score.update(Align.center(_hud_text(self._model)))
        field.update(Align.center(_field_panel(self._model)))


class StarfallGameEntry(TerminalGame):
    """Registry entry for Starfall."""

    @property
    def game_id(self) -> str:
        return "starfall"

    @property
    def title(self) -> str:
        return "Starfall"

    @property
    def description(self) -> str:
        return "Pilot an ASCII ship at the bottom of the screen, blasting waves of descending alien craft before they reach you."

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return StarfallScreen(return_to_menu)
