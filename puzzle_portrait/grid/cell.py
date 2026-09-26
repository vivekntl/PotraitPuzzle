"""A single mosaic cell with position, background color, and optional letter."""

from dataclasses import dataclass

from puzzle_portrait.grid.color import RGB


@dataclass(frozen=True, slots=True)
class Cell:
    row: int
    column: int
    color: RGB
    character: str | None = None

    def __post_init__(self) -> None:
        if self.character is None:
            return
        if not isinstance(self.character, str) or len(self.character) != 1:
            raise ValueError(
                f"character must be a single character or None, got {self.character!r}"
            )
