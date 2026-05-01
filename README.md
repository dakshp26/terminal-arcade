<h1 align="center">Terminal Arcade</h1>

<p align="center">
  <img src="assets/screenshot-title-card.png" alt="Terminal Arcade Games" />
</p>

<p align="center">
  <a href="https://github.com/dakshp26/terminal-arcade"><img src="https://img.shields.io/github/stars/dakshp26/terminal-arcade?style=social" alt="GitHub Stars" /></a>
  <img src="https://img.shields.io/badge/python-3.13%2B-blue.svg" alt="Python 3.13+" />
  <a href="https://github.com/Textualize/textual"><img src="https://img.shields.io/badge/TUI-Textual-purple" alt="Powered by Textual" /></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/linted%20with-ruff-orange" alt="Linted with Ruff" /></a>
</p>

<div align="center">
A collection of classic arcade games that run entirely in your terminal — no browser, no GUI, no dependencies beyond Python. It's a playground for learning terminal UI development with Textual and Rich — feel free to explore, tinker, and build on it. Play fully interactive ASCII games straight from the command line. Built with <a href="https://github.com/Textualize/textual">Textual</a> and <a href="https://github.com/Textualize/rich">Rich</a> — smooth keyboard input, live rendering, and zero latency.
</div>

<p></p>

<div align="center">
If you find it fun and interesting, consider giving it a ⭐ — it helps others discover the project.
</div>

---

## Games

<table>

<tr>
<td align="center" width="25%">

### Serpentine
<img src="assets/serpentine.png" alt="Serpentine" width="100%" />

Steer a growing snake around the screen to eat food. Avoid hitting walls or your own tail.

</td>
<td align="center" width="25%">

### Starfall
<img src="assets/starfall.png" alt="Starfall" width="100%" />

Pilot an ASCII ship at the bottom of the screen, blasting waves of descending alien craft before they reach you.

</td>
<td align="center" width="25%">

### Tic Tac Toe
<img src="assets/tic-tac-toe.png" alt="Tic Tac Toe" width="100%" />

Two-player classic. Take turns placing X and O; first to line up three in a row wins.

</td>
<td align="center" width="25%">

### Minefield
<img src="assets/minefield.png" alt="Minefield" width="100%" />

Uncover a grid hiding 25 mines using numbered clues. Flag every mine without triggering one.

</td>
</tr>

<tr>
<td align="center" width="25%">

### AsterAvoid
<img src="assets/asteravoid.png" alt="AsterAvoid" width="100%" />
Pilot a spacecraft across the bottom and dodge a relentless barrage of accelerating asteroids falling from above.
</td>
<td align="center" width="25%">

### Echo Chamber
<img src="assets/echo-chamber.png" alt="Echo Chamber" width="100%" />
Navigate a pitch-dark cave as a bat — pulse sonar to illuminate your surroundings, reach the exit before your echo fades and the cave bats find you.
</td>
</tr>
</table>

### More on the way...

The arcade is still being built. More games are queued up and dropping soon — stay tuned by watching and starring the repo (or better yet, contribute one).

---

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) — or pip

---

## Installation

```bash
# Clone the repo
git clone https://github.com/dakshp26/terminal-arcade.git
cd terminal-arcade

# Install dependencies and run
uv sync
uv run main.py
```

Or with pip:

```bash
pip install textual rich
python main.py
```

---

## Controls

| Action   | Keys                        |
|----------|-----------------------------|
| Move     | Arrow keys / WASD / hjkl    |
| Fire     | Space / ↑ / W               |
| Restart  | R                           |
| Menu     | Esc                         |
| Quit     | Ctrl+C                      |

---

## Project Structure

```
terminal_games/
├── app.py               # App root (Textual)
├── screens/
│   └── menu.py          # Game selection menu
└── games/
    ├── protocol.py      # TerminalGame interface
    ├── registry.py      # Game registry
    ├── serpentine/
    │   ├── model.py     # Pure game logic
    │   └── screen.py    # TUI screen
    ├── starfall/
    │   ├── model.py     # Pure game logic
    │   └── screen.py    # TUI screen
    ├── tictactoe/
    │   ├── model.py     # Pure game logic
    │   └── screen.py    # TUI screen
    ├── minefield/
    │   ├── model.py     # Pure game logic
    │   └── screen.py    # TUI screen
    ├── asteravoid/
    │   ├── model.py     # Pure game logic
    │   └── screen.py    # TUI screen
    └── echo_chamber/
        ├── model.py     # Pure game logic
        └── screen.py    # TUI screen
```

Game logic (`model.py`) is kept free of Textual/Rich imports so it stays independently testable.

---

## Adding a New Game

1. Create `terminal_games/games/<name>/` with `model.py` and `screen.py`.
2. Implement the `TerminalGame` protocol — `game_id`, `title`, `description`, `build_screen()`.
3. Register it in `terminal_games/games/registry.py` → `get_games()`.

That's it. The menu picks it up automatically.

---

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

---

## Contributing

Contributions are welcome. To add a game, fix a bug, or improve the TUI:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-game`
3. Make your changes and add tests
4. Open a pull request

Please keep game logic (model) free of UI imports so tests stay fast and framework-independent.

All contributions will be licensed under the license terms.

---

## License

See [LICENSE](LICENSE) for details.

This project is intended for personal and educational use only. It is not permitted to use this project for commercial purposes. The sole intention of this project is to showcase the development of terminal based games using python and open source libraries.
