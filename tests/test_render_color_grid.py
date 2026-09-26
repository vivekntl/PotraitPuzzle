import pytest
from PIL.Image import Image as PILImage

from puzzle_portrait.grid import ColorGrid, RGB
from puzzle_portrait.render import render_color_grid


def _sample_grid() -> ColorGrid:
    grid = ColorGrid(2, 2)
    grid[0, 0] = RGB(255, 0, 0)
    grid[0, 1] = RGB(0, 255, 0)
    grid[1, 0] = RGB(0, 0, 255)
    grid[1, 1] = RGB(255, 255, 0)
    return grid


def test_render_uses_configurable_cell_size() -> None:
    image = render_color_grid(_sample_grid(), cell_size=5)

    assert isinstance(image, PILImage)
    assert image.size == (10, 10)


def test_render_fills_cells_with_source_colors() -> None:
    image = render_color_grid(_sample_grid(), cell_size=4)

    assert image.getpixel((1, 1)) == (255, 0, 0)
    assert image.getpixel((5, 1)) == (0, 255, 0)
    assert image.getpixel((1, 5)) == (0, 0, 255)
    assert image.getpixel((5, 5)) == (255, 255, 0)


def test_render_optional_grid_lines_are_subtle_and_between_cells() -> None:
    line = RGB(48, 48, 48)
    image = render_color_grid(
        _sample_grid(),
        cell_size=4,
        grid_lines=True,
        grid_line_color=line,
    )

    assert image.getpixel((4, 1)) == (48, 48, 48)
    assert image.getpixel((1, 4)) == (48, 48, 48)
    assert image.getpixel((1, 1)) == (255, 0, 0)
    assert image.getpixel((5, 5)) == (255, 255, 0)


def test_render_without_grid_lines_keeps_solid_cells() -> None:
    image = render_color_grid(_sample_grid(), cell_size=4, grid_lines=False)

    assert image.getpixel((4, 1)) == (0, 255, 0)
    assert image.getpixel((1, 4)) == (0, 0, 255)


def test_render_rejects_non_positive_cell_size() -> None:
    with pytest.raises(ValueError, match="cell_size"):
        render_color_grid(_sample_grid(), cell_size=0)


def test_render_does_not_modify_grid() -> None:
    grid = _sample_grid()

    render_color_grid(grid, cell_size=3)

    assert grid[0, 0].color == RGB(255, 0, 0)
    assert grid[1, 1].color == RGB(255, 255, 0)
