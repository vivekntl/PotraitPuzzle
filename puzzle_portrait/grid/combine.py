"""Combine a color grid and a letter grid into one mosaic."""

from puzzle_portrait.grid.mosaic import Grid
from puzzle_portrait.wordsearch.letter_grid import EMPTY, LetterGrid

ColorGrid = Grid
MosaicGrid = Grid


def combine_grids(color_grid: ColorGrid, letter_grid: LetterGrid) -> MosaicGrid:
    """Merge matching grids, keeping color from one and letters from the other."""
    if color_grid.dimensions != letter_grid.dimensions:
        raise ValueError(
            "Grid dimensions must match, got "
            f"{color_grid.dimensions} and {letter_grid.dimensions}"
        )

    mosaic = MosaicGrid(color_grid.width, color_grid.height)
    for row in range(color_grid.height):
        for column in range(color_grid.width):
            mosaic[row, column] = color_grid[row, column].color
            letter = letter_grid[row, column]
            mosaic.set_character(row, column, letter if letter != EMPTY else None)

    return mosaic
