import pytest

from puzzle_portrait.wordsearch import (
    DOWN,
    DOWN_RIGHT,
    EMPTY,
    LEFT,
    RIGHT,
    UP_LEFT,
    LetterGrid,
    place_word,
)


def _snapshot(grid: LetterGrid) -> list[list[str]]:
    return [
        [grid[row, column] for column in range(grid.width)]
        for row in range(grid.height)
    ]


def test_place_word_writes_letters_on_empty_cells() -> None:
    grid = LetterGrid(5, 3)

    place_word(grid, "CAT", 1, 1, RIGHT)

    assert grid[1, 1] == "C"
    assert grid[1, 2] == "A"
    assert grid[1, 3] == "T"
    assert grid[1, 0] == EMPTY
    assert grid[1, 4] == EMPTY


def test_place_word_reuses_matching_occupied_letters() -> None:
    grid = LetterGrid(5, 3)
    grid[0, 1] = "A"
    grid[0, 2] = "T"

    place_word(grid, "CAT", 0, 0, RIGHT)

    assert grid[0, 0] == "C"
    assert grid[0, 1] == "A"
    assert grid[0, 2] == "T"


def test_place_word_rejects_overflow_without_changing_the_grid() -> None:
    grid = LetterGrid(5, 3)
    grid[0, 2] = "X"
    before = _snapshot(grid)

    with pytest.raises(ValueError, match="Cannot place"):
        place_word(grid, "CATS", 0, 2, RIGHT)

    assert _snapshot(grid) == before
    assert grid[0, 2] == "X"
    assert grid[0, 3] == EMPTY
    assert grid[0, 4] == EMPTY


def test_place_word_rejects_conflict_without_partial_writes() -> None:
    grid = LetterGrid(5, 3)
    grid[0, 2] = "X"
    before = _snapshot(grid)

    with pytest.raises(ValueError, match="Cannot place"):
        place_word(grid, "CAT", 0, 0, RIGHT)

    assert _snapshot(grid) == before
    assert grid[0, 0] == EMPTY
    assert grid[0, 1] == EMPTY
    assert grid[0, 2] == "X"


def test_place_word_works_left_down_and_diagonal() -> None:
    grid = LetterGrid(5, 5)

    place_word(grid, "HI", 0, 2, LEFT)
    place_word(grid, "GO", 1, 0, DOWN)
    place_word(grid, "OK", 2, 2, DOWN_RIGHT)
    place_word(grid, "NK", 4, 4, UP_LEFT)

    assert grid[0, 2] == "H"
    assert grid[0, 1] == "I"
    assert grid[1, 0] == "G"
    assert grid[2, 0] == "O"
    assert grid[2, 2] == "O"
    assert grid[3, 3] == "K"
    assert grid[4, 4] == "N"


def test_place_word_rejects_empty_word_without_changing_the_grid() -> None:
    grid = LetterGrid(3, 3)
    before = _snapshot(grid)

    with pytest.raises(ValueError, match="Cannot place"):
        place_word(grid, "", 1, 1, RIGHT)

    assert _snapshot(grid) == before
