"""Rectangular grid of characters, independent of image and mosaic types."""

EMPTY = ""


class LetterGrid:
    """A width-by-height grid of letters addressed as ``grid[row, column]``."""

    def __init__(self, width: int, height: int) -> None:
        if width < 1 or height < 1:
            raise ValueError(f"Grid size must be at least 1x1, got {width}x{height}")

        self._width = width
        self._height = height
        self._cells = [[EMPTY for _ in range(width)] for _ in range(height)]

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def dimensions(self) -> tuple[int, int]:
        return self._width, self._height

    def in_bounds(self, row: int, column: int) -> bool:
        return 0 <= row < self._height and 0 <= column < self._width

    def is_empty(self, row: int, column: int) -> bool:
        return self[row, column] == EMPTY

    def __getitem__(self, key: tuple[int, int]) -> str:
        row, column = self._require_in_bounds(key)
        return self._cells[row][column]

    def __setitem__(self, key: tuple[int, int], letter: str) -> None:
        row, column = self._require_in_bounds(key)
        self._cells[row][column] = self._require_letter(letter)

    def fill_empty(self, letter: str) -> None:
        """Write ``letter`` into every empty cell."""
        fill = self._require_letter(letter)
        if fill == EMPTY:
            return

        for row in range(self._height):
            for column in range(self._width):
                if self._cells[row][column] == EMPTY:
                    self._cells[row][column] = fill

    def _require_in_bounds(self, key: tuple[int, int]) -> tuple[int, int]:
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Grid indices must be (row, column)")
        row, column = key
        if not self.in_bounds(row, column):
            raise IndexError(
                f"Cell ({row}, {column}) is outside the {self._width}x{self._height} grid"
            )
        return row, column

    @staticmethod
    def _require_letter(letter: str) -> str:
        if not isinstance(letter, str) or len(letter) > 1:
            raise ValueError(f"Cell value must be a single character, got {letter!r}")
        return letter
