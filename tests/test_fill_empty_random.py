from puzzle_portrait.wordsearch import (
    EMPTY,
    LetterGrid,
    RIGHT,
    fill_count,
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


def test_fill_empty_random_percent_zero_leaves_empties() -> None:
    grid = LetterGrid(4, 1)
    grid[0, 0] = "A"

    fill_empty_random(grid, seed=3, percent=0)

    assert grid[0, 0] == "A"
    assert _all_cells(grid).count(EMPTY) == 3


def test_fill_empty_random_percent_fills_that_share() -> None:
    grid = LetterGrid(10, 1)

    fill_empty_random(grid, seed=8, percent=50)

    filled = sum(1 for cell in _all_cells(grid) if cell != EMPTY)
    assert filled == fill_count(10, 50)
    assert filled == 5


def test_generate_word_search_respects_fill_percent() -> None:
    puzzle = generate_word_search(
        5,
        1,
        ["HI"],
        directions=(RIGHT,),
        seed=0,
        fill_percent=0,
    )

    letters = [puzzle.grid[0, column] for column in range(5)]
    assert letters.count("H") == 1
    assert letters.count("I") == 1
    assert letters.count(EMPTY) == 3
