import pytest

from puzzle_portrait.wordsearch import (
    EMPTY,
    LetterGrid,
    Placement,
    can_place,
    place_word_randomly,
)


def _snapshot(grid: LetterGrid) -> list[list[str]]:
    return [
        [grid[row, column] for column in range(grid.width)]
        for row in range(grid.height)
    ]


def _letters_along(grid: LetterGrid, placement: Placement) -> str:
    letters = []
    for offset, _ in enumerate(placement.word):
        row = placement.row + offset * placement.direction.d_row
        column = placement.column + offset * placement.direction.d_column
        letters.append(grid[row, column])
    return "".join(letters)


def test_place_word_randomly_writes_the_word_and_describes_it() -> None:
    grid = LetterGrid(6, 6)

    placement = place_word_randomly(grid, "CAT", seed=7)

    assert isinstance(placement, Placement)
    assert placement.word == "CAT"
    assert can_place(
        grid, placement.word, placement.row, placement.column, placement.direction
    )
    assert _letters_along(grid, placement) == "CAT"


def test_place_word_randomly_is_reproducible_with_the_same_seed() -> None:
    first = LetterGrid(8, 8)
    second = LetterGrid(8, 8)

    placement_a = place_word_randomly(first, "HELLO", seed=42)
    placement_b = place_word_randomly(second, "HELLO", seed=42)

    assert placement_a == placement_b
    assert _snapshot(first) == _snapshot(second)


def test_place_word_randomly_can_choose_different_placements() -> None:
    placements = {
        place_word_randomly(LetterGrid(8, 8), "HI", seed=seed)
        for seed in range(20)
    }

    assert len(placements) > 1


def test_place_word_randomly_rejects_impossible_word_without_changes() -> None:
    grid = LetterGrid(3, 3)
    grid[1, 1] = "X"
    before = _snapshot(grid)

    with pytest.raises(ValueError, match="No valid placement"):
        place_word_randomly(grid, "TOOLONG", seed=1)

    assert _snapshot(grid) == before
    assert grid[0, 0] == EMPTY
    assert grid[1, 1] == "X"
