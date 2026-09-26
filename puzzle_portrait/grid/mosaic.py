"""Rectangular 2D mosaic grid of cells."""

from puzzle_portrait.grid.cell import Cell
from puzzle_portrait.grid.color import RGB

DEFAULT_COLOR = RGB(0, 0, 0)


class Grid:
    """A width-by-height grid of cells addressed as ``grid[row, column]``."""

    def __init__(
        self,
        width: int,
        height: int,
        color: RGB = DEFAULT_COLOR,
    ) -> None:
        if width < 1 or height < 1:
            raise ValueError(f"Grid size must be at least 1x1, got {width}x{height}")

        self._width = width
        self._height = height
        self._cells = [
            [Cell(row=row, column=column, color=color) for column in range(width)]
            for row in range(height)
        ]

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def dimensions(self) -> tuple[int, int]:
        return self._width, self._height

    def __getitem__(self, key: tuple[int, int]) -> Cell:
        row, column = self._unpack(key)
        return self._cells[row][column]

    def __setitem__(self, key: tuple[int, int], color: RGB) -> None:
        row, column = self._unpack(key)
        if not isinstance(color, RGB):
            raise TypeError(f"Cell color must be RGB, got {type(color).__name__}")
        existing = self._cells[row][column]
        self._cells[row][column] = Cell(
            row=row,
            column=column,
            color=color,
            character=existing.character,
        )

    def set_character(self, row: int, column: int, character: str | None) -> None:
        """Set the optional letter on a cell without changing its color."""
        row, column = self._unpack((row, column))
        existing = self._cells[row][column]
        self._cells[row][column] = Cell(
            row=row,
            column=column,
            color=existing.color,
            character=character,
        )

    def _unpack(self, key: tuple[int, int]) -> tuple[int, int]:
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Grid indices must be (row, column)")
        row, column = key
        if not (0 <= row < self._height and 0 <= column < self._width):
            raise IndexError(
                f"Cell ({row}, {column}) is outside the {self._width}x{self._height} grid"
            )
        return row, column
