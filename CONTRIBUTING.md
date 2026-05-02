# Contributing Guidelines

## Development

### Setup

```bash
git clone https://github.com/dakshp26/terminal-arcade.git
cd terminal-arcade
uv sync
uv run main.py
```

Or with pip:

```bash
pip install textual rich
python main.py
```

### Test and Lint Commands

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

---

## Steps to Contribute

Contributions are welcome. To add a game, fix a bug, or improve the TUI:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-game`
3. Make your changes and add tests
4. Open a pull request

Please keep game logic (model) free of UI imports so tests stay fast and framework-independent.

All contributions will be licensed under the license terms.
