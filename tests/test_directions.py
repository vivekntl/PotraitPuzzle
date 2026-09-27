import pytest

from puzzle_portrait.wordsearch import (
    BACKWARD_DIRECTIONS,
    DIRECTIONS,
    DOWN,
    DOWN_LEFT,
    DOWN_RIGHT,
    FORWARD_DIRECTIONS,
    LEFT,
    RIGHT,
    UP,
    UP_LEFT,
    UP_RIGHT,
    Direction,
    axis_of,
    direction_weights_from_axes,
    normalize_direction_weights,
    placement_directions,
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


def test_axis_of_classifies_neighbor_steps() -> None:
    assert axis_of(RIGHT) == "horizontal"
    assert axis_of(LEFT) == "horizontal"
    assert axis_of(DOWN) == "vertical"
    assert axis_of(UP) == "vertical"
    assert axis_of(DOWN_RIGHT) == "diagonal"


def test_direction_weights_from_axes_expand_to_all_eight() -> None:
    weights = direction_weights_from_axes(horizontal=2, vertical=0.5, diagonal=0)

    assert weights[RIGHT] == 2
    assert weights[LEFT] == 2
    assert weights[DOWN] == 0.5
    assert weights[UP_LEFT] == 0


def test_forward_directions_are_left_to_right_and_top_to_bottom() -> None:
    assert FORWARD_DIRECTIONS == (RIGHT, DOWN, DOWN_RIGHT, UP_RIGHT)
    assert BACKWARD_DIRECTIONS == (LEFT, UP, DOWN_LEFT, UP_LEFT)
    assert set(FORWARD_DIRECTIONS) | set(BACKWARD_DIRECTIONS) == set(DIRECTIONS)


def test_placement_directions_toggle_backwards() -> None:
    assert placement_directions(allow_backwards=False) == FORWARD_DIRECTIONS
    assert placement_directions(allow_backwards=True) == DIRECTIONS


def test_normalize_direction_weights_keeps_axis_shares() -> None:
    raw = direction_weights_from_axes(horizontal=1, vertical=1, diagonal=2)
    forward = normalize_direction_weights(raw, FORWARD_DIRECTIONS)

    assert forward[RIGHT] == 1
    assert forward[DOWN] == 1
    assert forward[DOWN_RIGHT] == 1
    assert forward[UP_RIGHT] == 1
    assert sum(forward[direction] for direction in FORWARD_DIRECTIONS if axis_of(direction) == "diagonal") == 2


def test_direction_weights_from_axes_reject_negatives() -> None:
    with pytest.raises(ValueError, match="weights"):
        direction_weights_from_axes(horizontal=-0.1)
