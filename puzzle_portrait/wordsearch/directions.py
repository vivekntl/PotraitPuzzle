"""Eight standard word-search directions as row and column deltas."""

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Direction:
    """One step on the grid: ``(row + d_row, column + d_column)``."""

    d_row: int
    d_column: int


RIGHT = Direction(0, 1)
LEFT = Direction(0, -1)
DOWN = Direction(1, 0)
UP = Direction(-1, 0)
DOWN_RIGHT = Direction(1, 1)
DOWN_LEFT = Direction(1, -1)
UP_RIGHT = Direction(-1, 1)
UP_LEFT = Direction(-1, -1)

DIRECTIONS: tuple[Direction, ...] = (
    RIGHT,
    LEFT,
    DOWN,
    UP,
    DOWN_RIGHT,
    DOWN_LEFT,
    UP_RIGHT,
    UP_LEFT,
)

FORWARD_DIRECTIONS: tuple[Direction, ...] = (
    RIGHT,
    DOWN,
    DOWN_RIGHT,
    UP_RIGHT,
)
BACKWARD_DIRECTIONS: tuple[Direction, ...] = (
    LEFT,
    UP,
    DOWN_LEFT,
    UP_LEFT,
)

HORIZONTAL_DIRECTIONS: tuple[Direction, ...] = (RIGHT, LEFT)
VERTICAL_DIRECTIONS: tuple[Direction, ...] = (DOWN, UP)
DIAGONAL_DIRECTIONS: tuple[Direction, ...] = (
    DOWN_RIGHT,
    DOWN_LEFT,
    UP_RIGHT,
    UP_LEFT,
)


def placement_directions(*, allow_backwards: bool) -> tuple[Direction, ...]:
    """Return the four forward directions, or all eight when backwards is on."""
    if allow_backwards:
        return DIRECTIONS
    return FORWARD_DIRECTIONS


def axis_of(direction: Direction) -> str:
    """Return ``horizontal``, ``vertical``, or ``diagonal`` for ``direction``."""
    if direction.d_row == 0:
        return "horizontal"
    if direction.d_column == 0:
        return "vertical"
    return "diagonal"


def direction_weights_from_axes(
    horizontal: float = 1.0,
    vertical: float = 1.0,
    diagonal: float = 1.0,
) -> dict[Direction, float]:
    """Expand axis weights onto the eight standard directions."""
    if min(horizontal, vertical, diagonal) < 0:
        raise ValueError("Direction weights must be zero or positive")
    weights = {direction: horizontal for direction in HORIZONTAL_DIRECTIONS}
    weights.update({direction: vertical for direction in VERTICAL_DIRECTIONS})
    weights.update({direction: diagonal for direction in DIAGONAL_DIRECTIONS})
    return weights


def normalize_direction_weights(
    weights: Mapping[Direction, float],
    allowed: Sequence[Direction],
) -> dict[Direction, float]:
    """Scale axis weights so the axis share matches the control, not the direction count.

    Horizontal=1, vertical=1, diagonal=2 means about 25% / 25% / 50% of words,
    even when two diagonal directions are allowed and only one horizontal.
    """
    counts = Counter(axis_of(direction) for direction in allowed)
    normalized: dict[Direction, float] = {}
    for direction in allowed:
        raw = weights.get(direction, 1.0)
        if raw < 0:
            raise ValueError(f"Direction weight must be >= 0, got {raw}")
        count = counts[axis_of(direction)]
        normalized[direction] = raw / count if count else 0.0
    return normalized
