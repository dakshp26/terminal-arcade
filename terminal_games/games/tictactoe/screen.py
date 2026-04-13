"""Tic Tac Toe Textual screen: input and view over ``TicTacToeModel``."""

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
from terminal_games.games.tictactoe.model import TicTacToeModel


def _ttt_field_panel(model: TicTacToeModel) -> Panel:
    t = Text()
    t.append("┌───┬───┬───┐\n")
    for row in range(3):
        t.append("│")
        for col in range(3):
            cell = model.board[row][col]
            is_cursor = row == model.cursor_row and col == model.cursor_col
            if cell == "X":
                style = theme.TTT_X_CURSOR if is_cursor else theme.TTT_X
            elif cell == "O":
                style = theme.TTT_O_CURSOR if is_cursor else theme.TTT_O
            else:
                style = theme.TTT_EMPTY_CURSOR if is_cursor else theme.TTT_EMPTY
            t.append(f" {cell} ", style=style)
            t.append("│")
        if row < 2:
            t.append("\n├───┼───┼───┤\n")
    t.append("\n└───┴───┴───┘")
    return Panel.fit(t, border_style=theme.TICTACTOE_ACCENT)


def _status_text(model: TicTacToeModel) -> Text:
    t = Text()
    if model.game_over:
        if model.winner:
            player_style = theme.TTT_X if model.winner == "X" else theme.TTT_O
            t.append("Player ", style=theme.LABEL)
            t.append(model.winner, style=player_style)
            t.append(" wins!", style=theme.WIN)
        else:
            t.append("Draw!", style=theme.DRAW)
        t.append("  — press ", style=theme.LABEL)
        t.append("R", style=theme.RESTART_KEY)
        t.append(" to restart", style=theme.LABEL)
    else:
        player_style = theme.TTT_X if model.current_player == "X" else theme.TTT_O
        t.append("Player ", style=theme.LABEL)
        t.append(model.current_player, style=player_style)
        t.append("'s turn", style=theme.LABEL)
        t.append("  ·  ", style=theme.LABEL)
        t.append("arrows/WASD move · Enter/Space place · Esc menu", style=theme.LABEL)
    return t


class TicTacToeScreen(Screen[None]):
    """Play Tic Tac Toe; Esc returns to menu, R restarts."""

    BINDINGS = [
        Binding("escape", "back", "Menu"),
        Binding("r", "restart", "Restart"),
    ]

    def __init__(self, return_to_menu: ReturnToMenu) -> None:
        super().__init__()
        self._return_to_menu = return_to_menu
        self._model = TicTacToeModel.new()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                Align.center(Text("Tic Tac Toe", style=theme.TICTACTOE_TITLE)),
                id="game_title",
            )
            yield Static(Align.center(_status_text(self._model)), id="ttt_status")
            yield Static(Align.center(_ttt_field_panel(self._model)), id="ttt_field")
            yield Footer()

    def on_mount(self) -> None:
        self._refresh_view()

    def on_key(self, event: events.Key) -> None:
        if self._model.game_over:
            return
        key = event.key
        if key in ("up", "w"):
            self._model.move_cursor(-1, 0)
            self._refresh_view()
        elif key in ("down", "s"):
            self._model.move_cursor(1, 0)
            self._refresh_view()
        elif key in ("left", "a"):
            self._model.move_cursor(0, -1)
            self._refresh_view()
        elif key in ("right", "d"):
            self._model.move_cursor(0, 1)
            self._refresh_view()
        elif key in ("enter", "space"):
            if self._model.place():
                self._refresh_view()

    def action_back(self) -> None:
        self._return_to_menu()

    def action_restart(self) -> None:
        self._model.reset()
        self._refresh_view()

    def _refresh_view(self) -> None:
        self.query_one("#ttt_status", Static).update(Align.center(_status_text(self._model)))
        self.query_one("#ttt_field", Static).update(Align.center(_ttt_field_panel(self._model)))


class TicTacToeGameEntry(TerminalGame):
    """Registry entry for Tic Tac Toe."""

    @property
    def game_id(self) -> str:
        return "tictactoe"

    @property
    def title(self) -> str:
        return "Tic Tac Toe"

    @property
    def description(self) -> str:
        return "Two-player classic. Take turns placing X and O; first to line up three in a row wins."

    def build_screen(self, return_to_menu: ReturnToMenu) -> Screen[None]:
        return TicTacToeScreen(return_to_menu)
