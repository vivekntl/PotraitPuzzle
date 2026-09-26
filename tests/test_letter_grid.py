import pytest

from puzzle_portrait.wordsearch import EMPTY, LetterGrid


def test_create_letter_grid_has_requested_dimensions() -> None:
    grid = LetterGrid(5, 3)

    assert grid.width == 5
    assert grid.height == 3
    assert grid.dimensions == (5, 3)


def test_new_letter_grid_cells_are_empty() -> None:
    grid = LetterGrid(2, 2)

    assert grid[0, 0] == EMPTY
    assert grid.is_empty(0, 1)
    assert grid.is_empty(1, 0)
    assert grid.is_empty(1, 1)


def test_get_and_set_cell() -> None:
    grid = LetterGrid(3, 2)
    grid[1, 2] = "Q"

    assert grid[1, 2] == "Q"
    assert not grid.is_empty(1, 2)
    assert grid[0, 0] == EMPTY


def test_in_bounds_checks_coordinates() -> None:
    grid = LetterGrid(3, 2)

    assert grid.in_bounds(0, 0)
    assert grid.in_bounds(1, 2)
    assert not grid.in_bounds(2, 0)
    assert not grid.in_bounds(0, 3)
    assert not grid.in_bounds(-1, 0)


def test_get_and_set_out_of_bounds_raise() -> None:
    grid = LetterGrid(2, 2)

    with pytest.raises(IndexError, match="outside"):
        grid[2, 0]
    with pytest.raises(IndexError, match="outside"):
        grid[0, 2] = "A"


def test_fill_empty_writes_only_unoccupied_cells() -> None:
    grid = LetterGrid(3, 2)
    grid[0, 1] = "W"

    grid.fill_empty("X")

    assert grid[0, 0] == "X"
    assert grid[0, 1] == "W"
    assert grid[0, 2] == "X"
    assert grid[1, 0] == "X"
    assert grid[1, 1] == "X"
    assert grid[1, 2] == "X"


def test_create_letter_grid_rejects_non_positive_size() -> None:
    with pytest.raises(ValueError, match="1x1"):
        LetterGrid(0, 4)
    with pytest.raises(ValueError, match="1x1"):
        LetterGrid(3, 0)


def test_set_rejects_multi_character_value() -> None:
    grid = LetterGrid(1, 1)

    with pytest.raises(ValueError, match="single character"):
        grid[0, 0] = "AB"
