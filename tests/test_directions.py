from puzzle_portrait.wordsearch import (
    DIRECTIONS,
    DOWN,
    DOWN_LEFT,
    DOWN_RIGHT,
    LEFT,
    RIGHT,
    UP,
    UP_LEFT,
    UP_RIGHT,
    Direction,
)


def test_eight_standard_directions() -> None:
    assert len(DIRECTIONS) == 8
    assert len(set(DIRECTIONS)) == 8


def test_horizontal_deltas() -> None:
    assert RIGHT == Direction(0, 1)
    assert LEFT == Direction(0, -1)


def test_vertical_deltas() -> None:
    assert DOWN == Direction(1, 0)
    assert UP == Direction(-1, 0)


def test_diagonal_deltas() -> None:
    assert DOWN_RIGHT == Direction(1, 1)
    assert DOWN_LEFT == Direction(1, -1)
    assert UP_RIGHT == Direction(-1, 1)
    assert UP_LEFT == Direction(-1, -1)


def test_directions_are_the_eight_neighbor_steps() -> None:
    deltas = {(direction.d_row, direction.d_column) for direction in DIRECTIONS}

    assert (0, 0) not in deltas
    assert deltas == {
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    }
    assert all(
        direction.d_row in (-1, 0, 1) and direction.d_column in (-1, 0, 1)
        for direction in DIRECTIONS
    )
