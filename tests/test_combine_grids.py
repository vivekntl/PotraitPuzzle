import pytest

from puzzle_portrait.grid import ColorGrid, RGB, combine_grids
from puzzle_portrait.wordsearch import LetterGrid


def test_combine_grids_preserves_color_and_letter() -> None:
    colors = ColorGrid(2, 2)
    colors[0, 0] = RGB(10, 20, 30)
    colors[0, 1] = RGB(40, 50, 60)
    colors[1, 0] = RGB(70, 80, 90)
    colors[1, 1] = RGB(100, 110, 120)

    letters = LetterGrid(2, 2)
    letters[0, 0] = "C"
    letters[1, 1] = "T"

    mosaic = combine_grids(colors, letters)

    assert mosaic.dimensions == (2, 2)
    assert mosaic[0, 0].color == RGB(10, 20, 30)
    assert mosaic[0, 0].character == "C"
    assert mosaic[0, 1].color == RGB(40, 50, 60)
    assert mosaic[0, 1].character is None
    assert mosaic[1, 0].color == RGB(70, 80, 90)
    assert mosaic[1, 0].character is None
    assert mosaic[1, 1].color == RGB(100, 110, 120)
    assert mosaic[1, 1].character == "T"


def test_combine_grids_rejects_mismatched_dimensions() -> None:
    colors = ColorGrid(3, 2)
    letters = LetterGrid(2, 2)

    with pytest.raises(ValueError, match="dimensions must match"):
        combine_grids(colors, letters)


def test_combine_grids_does_not_modify_sources() -> None:
    colors = ColorGrid(1, 2, color=RGB(1, 2, 3))
    letters = LetterGrid(1, 2)
    letters[1, 0] = "A"

    combine_grids(colors, letters)

    assert colors[0, 0].color == RGB(1, 2, 3)
    assert colors[0, 0].character is None
    assert letters[0, 0] == ""
    assert letters[1, 0] == "A"
