"""Central list of games — add new games here (open/closed extension point)."""

from __future__ import annotations

from terminal_games.games.asteravoid.screen import AsterAvoidGameEntry
from terminal_games.games.echo_chamber.screen import EchoChamberGameEntry
from terminal_games.games.floodgate.screen import FloodgateGameEntry
from terminal_games.games.minefield.screen import MinefieldGameEntry
from terminal_games.games.protocol import TerminalGame
from terminal_games.games.serpentine.screen import SerpentineGameEntry
from terminal_games.games.starfall.screen import StarfallGameEntry
from terminal_games.games.tictactoe.screen import TicTacToeGameEntry


def get_games() -> list[TerminalGame]:
    """Return menu order of available games."""
    return [
        SerpentineGameEntry(),
        StarfallGameEntry(),
        TicTacToeGameEntry(),
        MinefieldGameEntry(),
        AsterAvoidGameEntry(),
        EchoChamberGameEntry(),
        FloodgateGameEntry(),
    ]
