from puzzle_portrait.wordsearch import (
    EMPTY,
    LetterGrid,
    fill_empty_random,
    generate_word_search,
)
from puzzle_portrait.wordsearch.fill import ALPHABET


def _all_cells(grid: LetterGrid) -> list[str]:
    return [
        grid[row, column]
        for row in range(grid.height)
        for column in range(grid.width)
    ]


def test_fill_empty_random_leaves_no_empty_cells() -> None:
    grid = LetterGrid(4, 3)
    grid[1, 1] = "Q"

    fill_empty_random(grid, seed=9)

    assert all(cell != EMPTY for cell in _all_cells(grid))
    assert all(cell in ALPHABET for cell in _all_cells(grid))
    assert grid[1, 1] == "Q"


def test_fill_empty_random_is_deterministic_with_the_same_seed() -> None:
    first = LetterGrid(5, 2)
    second = LetterGrid(5, 2)
    first[0, 0] = "Z"
    second[0, 0] = "Z"

    fill_empty_random(first, seed=21)
    fill_empty_random(second, seed=21)

    assert _all_cells(first) == _all_cells(second)


def test_generate_word_search_fills_every_empty_cell() -> None:
    puzzle = generate_word_search(6, 5, ["CAT", "DOG"], seed=4)

    assert all(not puzzle.grid.is_empty(row, column)
               for row in range(puzzle.grid.height)
               for column in range(puzzle.grid.width))
    assert all(
        puzzle.grid[row, column] in ALPHABET
        for row in range(puzzle.grid.height)
        for column in range(puzzle.grid.width)
    )
    for placement in puzzle.placements:
        for offset, letter in enumerate(placement.word):
            row = placement.row + offset * placement.direction.d_row
            column = placement.column + offset * placement.direction.d_column
            assert puzzle.grid[row, column] == letter
