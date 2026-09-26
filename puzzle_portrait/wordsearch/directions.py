"""Eight standard word-search directions as row and column deltas."""

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
