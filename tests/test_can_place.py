from puzzle_portrait.wordsearch import (
    DIRECTIONS,
    DOWN,
    DOWN_LEFT,
    DOWN_RIGHT,
    EMPTY,
    LEFT,
    RIGHT,
    UP,
    UP_LEFT,
    UP_RIGHT,
    LetterGrid,
    can_place,
)


def test_can_place_on_empty_cells_when_the_word_fits() -> None:
    grid = LetterGrid(5, 3)

    assert can_place(grid, "CAT", 1, 1, RIGHT)


def test_can_place_rejects_word_that_leaves_the_grid() -> None:
    grid = LetterGrid(5, 3)

    assert not can_place(grid, "CATS", 0, 2, RIGHT)
    assert not can_place(grid, "CAT", 0, 0, LEFT)
    assert not can_place(grid, "CAT", 1, 2, DOWN)
    assert not can_place(grid, "CAT", 1, 2, UP)


def test_can_place_rejects_start_outside_the_grid() -> None:
    grid = LetterGrid(4, 4)

    assert not can_place(grid, "A", -1, 0, RIGHT)
    assert not can_place(grid, "A", 0, 4, RIGHT)
    assert not can_place(grid, "HI", 4, 0, DOWN)


def test_can_place_allows_matching_occupied_letters() -> None:
    grid = LetterGrid(5, 3)
    grid[0, 1] = "A"
    grid[0, 2] = "T"

    assert can_place(grid, "CAT", 0, 0, RIGHT)
    assert can_place(grid, "AT", 0, 1, RIGHT)


def test_can_place_rejects_conflicting_occupied_letters() -> None:
    grid = LetterGrid(5, 3)
    grid[0, 1] = "X"

    assert not can_place(grid, "CAT", 0, 0, RIGHT)


def test_can_place_does_not_modify_the_grid() -> None:
    grid = LetterGrid(4, 2)
    grid[0, 1] = "B"
    before = [[grid[row, column] for column in range(4)] for row in range(2)]

    can_place(grid, "ABC", 0, 0, RIGHT)
    can_place(grid, "XYZ", 0, 2, RIGHT)

    after = [[grid[row, column] for column in range(4)] for row in range(2)]
    assert after == before
    assert grid[0, 0] == EMPTY
    assert grid[0, 1] == "B"


def test_can_place_works_in_all_eight_directions() -> None:
    grid = LetterGrid(5, 5)
    start = (2, 2)
    word = "AB"

    for direction in DIRECTIONS:
        assert can_place(grid, word, *start, direction)


def test_can_place_diagonals_respect_bounds_and_letters() -> None:
    grid = LetterGrid(3, 3)
    grid[1, 1] = "O"

    assert can_place(grid, "NO", 0, 0, DOWN_RIGHT)
    assert can_place(grid, "SO", 0, 2, DOWN_LEFT)
    assert can_place(grid, "TO", 2, 0, UP_RIGHT)
    assert can_place(grid, "WO", 2, 2, UP_LEFT)
    assert not can_place(grid, "TOOL", 2, 0, UP_RIGHT)
    assert not can_place(grid, "XY", 0, 0, DOWN_RIGHT)


def test_can_place_single_letter_at_an_edge_cell() -> None:
    grid = LetterGrid(2, 2)

    assert can_place(grid, "Z", 0, 0, LEFT)
    assert can_place(grid, "Z", 1, 1, DOWN)
    grid[1, 1] = "Z"
    assert can_place(grid, "Z", 1, 1, UP)
    grid[1, 1] = "Y"
    assert not can_place(grid, "Z", 1, 1, UP)


def test_can_place_rejects_empty_word() -> None:
    grid = LetterGrid(3, 3)

    assert not can_place(grid, "", 1, 1, RIGHT)
