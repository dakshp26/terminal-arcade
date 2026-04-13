"""Centralised colour / style palette for the terminal-games launcher.

Import from here instead of scattering literal style strings across screens.
Each screen should only reference these names — never raw colour strings.
"""

from __future__ import annotations

# ── Shared HUD / status colours ───────────────────────────────────────────────

LABEL = "dim"           # dim labels, separators, and hint text
SCORE_VALUE = "bold cyan"
LIVES_VALUE = "bold green"
WAVE_VALUE = "bold yellow"

# ── End-of-game ───────────────────────────────────────────────────────────────

GAME_OVER = "bold red"
WIN = "bold bright_green"
DRAW = "bold yellow"
RESTART_KEY = "bold yellow"     # the "R" key highlight in prompts

# ── Menu colours ─────────────────────────────────────────────────────────────

MENU_ACCENT = "cyan"            # panel border, rule
MENU_TITLE = "bold cyan"        # ASCII art
MENU_GAME_TITLE = "bold bright_cyan"  # game name in the option list

# ── Per-game accent colours (drives title text + panel border) ────────────────

SERPENTINE_ACCENT = "green"
SERPENTINE_TITLE = "bold bright_green"

STARFALL_ACCENT = "magenta"
STARFALL_TITLE = "bold magenta"

TICTACTOE_ACCENT = "bright_white"
TICTACTOE_TITLE = "bold bright_white"

MINEFIELD_ACCENT = "bright_cyan"
MINEFIELD_TITLE = "bold bright_cyan"

# ── Tic Tac Toe player colours ────────────────────────────────────────────────

TTT_X = "bold bright_blue"
TTT_X_CURSOR = "bold bright_blue reverse"
TTT_O = "bold bright_red"
TTT_O_CURSOR = "bold bright_red reverse"
TTT_EMPTY = "dim"
TTT_EMPTY_CURSOR = "bold bright_white reverse"

# ── Serpentine cell colours ───────────────────────────────────────────────────
# snake body → SERPENTINE_ACCENT, snake head → SERPENTINE_TITLE

SERPENTINE_FOOD = "bold red"        # food pellet (*)

# ── Starfall cell colours ─────────────────────────────────────────────────────
# alien → STARFALL_TITLE, alien bullet → GAME_OVER

STARFALL_SHIP_BODY = "bold cyan"        # player ship wings (=)
STARFALL_SHIP_NOSE = "bold bright_cyan" # player ship centre (^)
STARFALL_BULLET_UP = "bold yellow"      # player bullet (|)

# ── Minefield colours ─────────────────────────────────────────────────────────
# number cells (1-8) as literals in screen.py

MINEFIELD_DANGER = "bold bright_red"    # flag count, BOOM!, exposed mine (*)
