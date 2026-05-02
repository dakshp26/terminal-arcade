"""Textual application root."""

from __future__ import annotations

from textual.app import App

from terminal_games.games.registry import get_games
from terminal_games.screens.menu import MenuScreen


class TerminalGamesApp(App[None]):
    """Pushes the game menu on startup."""

    TITLE = "Terminal Games"

    CSS = """
    #title {
        margin: 1 2;
        height: auto;
    }
    #menu_rule {
        margin: 0 2;
    }
    #game_list {
        margin: 0 2 1 2;
    }
    #game_title {
        margin: 1 2 0 2;
        height: auto;
        content-align: center top;
    }
    #score_line {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    #si_score_line {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #si_field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    #ttt_status {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #ttt_field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    #mf_status {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #mf_field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    #av_status {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #av_field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    #ec_status {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #ec_field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    #fg_status {
        margin: 0 2;
        height: auto;
        content-align: center top;
    }
    #fg_field {
        margin: 0 2 1 2;
        height: auto;
        content-align: center top;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(MenuScreen(get_games()))


def run_app() -> None:
    TerminalGamesApp().run()
