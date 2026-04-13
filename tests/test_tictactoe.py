"""Tic Tac Toe game tests."""

from __future__ import annotations

from textual.screen import Screen

from terminal_games.games.tictactoe.model import TicTacToeModel
from terminal_games.games.tictactoe.screen import TicTacToeGameEntry, TicTacToeScreen


def test_tictactoe_game_entry_builds_screen() -> None:
    entry = TicTacToeGameEntry()
    assert entry.game_id == "tictactoe"
    assert entry.title

    screen = entry.build_screen(lambda: None)
    assert isinstance(screen, Screen)
    assert isinstance(screen, TicTacToeScreen)


def test_new_model_initial_state() -> None:
    model = TicTacToeModel.new()
    assert model.current_player == "X"
    assert model.winner is None
    assert not model.draw
    assert not model.game_over
    assert all(model.board[r][c] == " " for r in range(3) for c in range(3))


def test_place_marks_board_and_alternates_player() -> None:
    model = TicTacToeModel.new()
    model.cursor_row, model.cursor_col = 0, 0
    assert model.place() is True
    assert model.board[0][0] == "X"
    assert model.current_player == "O"

    model.cursor_row, model.cursor_col = 1, 1
    assert model.place() is True
    assert model.board[1][1] == "O"
    assert model.current_player == "X"


def test_place_occupied_cell_rejected() -> None:
    model = TicTacToeModel.new()
    model.cursor_row, model.cursor_col = 0, 0
    model.place()  # X at (0,0)
    model.cursor_row, model.cursor_col = 0, 0
    assert model.place() is False  # O cannot overwrite X
    assert model.board[0][0] == "X"
    assert model.current_player == "O"  # turn did not advance


def test_place_after_game_over_rejected() -> None:
    model = TicTacToeModel.new()
    # X wins top row
    for col in range(3):
        model.cursor_row, model.cursor_col = 0, col
        model.place()
        if model.game_over:
            break
        model.cursor_row, model.cursor_col = 1, col
        model.place()
    assert model.game_over
    model.cursor_row, model.cursor_col = 2, 2
    assert model.place() is False


def test_row_win_detected() -> None:
    model = TicTacToeModel.new()
    # X: (0,0),(0,1),(0,2) — O plays off to the side each turn
    moves = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
    for r, c in moves:
        model.cursor_row, model.cursor_col = r, c
        model.place()
    assert model.winner == "X"
    assert model.game_over


def test_column_win_detected() -> None:
    model = TicTacToeModel.new()
    # X: col 0 rows 0,1,2 — O plays col 1
    moves = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
    for r, c in moves:
        model.cursor_row, model.cursor_col = r, c
        model.place()
    assert model.winner == "X"
    assert model.game_over


def test_diagonal_win_detected() -> None:
    model = TicTacToeModel.new()
    # X: (0,0),(1,1),(2,2) — O plays top-right area
    moves = [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]
    for r, c in moves:
        model.cursor_row, model.cursor_col = r, c
        model.place()
    assert model.winner == "X"
    assert model.game_over


def test_anti_diagonal_win_detected() -> None:
    model = TicTacToeModel.new()
    # X: (0,2),(1,1),(2,0) — O plays left column
    moves = [(0, 2), (0, 0), (1, 1), (1, 0), (2, 0)]
    for r, c in moves:
        model.cursor_row, model.cursor_col = r, c
        model.place()
    assert model.winner == "X"
    assert model.game_over


def test_draw_detected() -> None:
    model = TicTacToeModel.new()
    # Known draw sequence:
    # X O X
    # X O X
    # O X O
    draw_moves = [
        (0, 0), (0, 1), (0, 2),
        (1, 1), (1, 0), (2, 0),
        (1, 2), (2, 2), (2, 1),
    ]
    for r, c in draw_moves:
        model.cursor_row, model.cursor_col = r, c
        model.place()
    assert model.draw
    assert model.winner is None
    assert model.game_over


def test_move_cursor_wraps() -> None:
    model = TicTacToeModel.new()
    model.cursor_row, model.cursor_col = 0, 0
    model.move_cursor(-1, 0)
    assert model.cursor_row == 2  # wraps to bottom
    model.move_cursor(0, -1)
    assert model.cursor_col == 2  # wraps to right


def test_reset_restores_initial_state() -> None:
    model = TicTacToeModel.new()
    model.cursor_row, model.cursor_col = 0, 0
    model.place()
    model.cursor_row, model.cursor_col = 1, 1
    model.place()
    model.reset()
    assert model.current_player == "X"
    assert model.winner is None
    assert not model.draw
    assert not model.game_over
    assert all(model.board[r][c] == " " for r in range(3) for c in range(3))


def test_render_lines_reflects_board() -> None:
    model = TicTacToeModel.new()
    model.cursor_row, model.cursor_col = 0, 0
    model.place()  # X at top-left
    lines = model.render_lines()
    assert len(lines) == 3
    assert lines[0][0] == "X"
