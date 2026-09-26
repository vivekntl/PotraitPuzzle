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


def _center_has_color(image: PILImage, color: tuple[int, int, int], box: int = 8) -> bool:
    cx, cy = image.size[0] // 2, image.size[1] // 2
    for y in range(cy - box, cy + box + 1):
        for x in range(cx - box, cx + box + 1):
            if image.getpixel((x, y)) == color:
                return True
    return False


def test_render_draws_letter_in_cell_center() -> None:
    grid = ColorGrid(1, 1, color=RGB(0, 0, 0))
    grid.set_character(0, 0, "A")

    image = render_color_grid(
        grid,
        cell_size=32,
        font_size=20,
        text_color=RGB(255, 255, 255),
        auto_text_color=False,
    )

    assert _center_has_color(image, (255, 255, 255))
    assert image.getpixel((0, 0)) == (0, 0, 0)


def test_render_can_skip_letters() -> None:
    grid = ColorGrid(1, 1, color=RGB(0, 128, 0))
    grid.set_character(0, 0, "A")

    image = render_color_grid(grid, cell_size=16, draw_letters=False)

    assert image.getpixel((8, 8)) == (0, 128, 0)


def test_render_uses_single_text_color() -> None:
    grid = ColorGrid(2, 1, color=RGB(0, 0, 0))
    grid.set_character(0, 0, "X")
    grid.set_character(0, 1, "Y")

    image = render_color_grid(
        grid,
        cell_size=32,
        font_size=18,
        text_color=RGB(255, 0, 0),
        auto_text_color=False,
    )

    left = image.crop((0, 0, 32, 32))
    right = image.crop((32, 0, 64, 32))
    assert _center_has_color(left, (255, 0, 0))
    assert _center_has_color(right, (255, 0, 0))


def test_render_rejects_non_positive_font_size() -> None:
    with pytest.raises(ValueError, match="font_size"):
        render_color_grid(_sample_grid(), font_size=0)
