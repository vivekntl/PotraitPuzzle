"""A single mosaic cell with position and background color."""

from dataclasses import dataclass

from puzzle_portrait.grid.color import RGB


@dataclass(frozen=True, slots=True)
class Cell:
    row: int
    column: int
    color: RGB
