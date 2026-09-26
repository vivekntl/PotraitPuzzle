from puzzle_portrait.grid import ColorGrid, RGB
from puzzle_portrait.render import (
    contrasting_text_color,
    relative_luminance,
    render_color_grid,
)
from puzzle_portrait.render.contrast import DARK_TEXT, LIGHT_TEXT


def test_dark_background_selects_light_text() -> None:
    assert relative_luminance(RGB(0, 0, 0)) < 0.55
    assert contrasting_text_color(RGB(0, 0, 0)) == LIGHT_TEXT
    assert contrasting_text_color(RGB(20, 20, 80)) == LIGHT_TEXT


def test_light_background_selects_dark_text() -> None:
    assert relative_luminance(RGB(255, 255, 255)) >= 0.55
    assert contrasting_text_color(RGB(255, 255, 255)) == DARK_TEXT
    assert contrasting_text_color(RGB(255, 255, 0)) == DARK_TEXT


def test_render_auto_text_color_follows_tile_luminance() -> None:
    grid = ColorGrid(2, 1)
    grid[0, 0] = RGB(0, 0, 0)
    grid[0, 1] = RGB(255, 255, 255)
    grid.set_character(0, 0, "A")
    grid.set_character(0, 1, "B")

    image = render_color_grid(grid, cell_size=32, font_size=18, auto_text_color=True)
    left = image.crop((0, 0, 32, 32))
    right = image.crop((32, 0, 64, 32))

    assert _center_has_color(left, (LIGHT_TEXT.red, LIGHT_TEXT.green, LIGHT_TEXT.blue))
    assert _center_has_color(right, (DARK_TEXT.red, DARK_TEXT.green, DARK_TEXT.blue))


def test_render_can_disable_auto_text_color() -> None:
    grid = ColorGrid(1, 1, color=RGB(255, 255, 255))
    grid.set_character(0, 0, "A")

    image = render_color_grid(
        grid,
        cell_size=32,
        font_size=18,
        auto_text_color=False,
        text_color=RGB(255, 0, 0),
    )

    assert _center_has_color(image, (255, 0, 0))


def _center_has_color(image, color: tuple[int, int, int], box: int = 8) -> bool:
    cx, cy = image.size[0] // 2, image.size[1] // 2
    for y in range(cy - box, cy + box + 1):
        for x in range(cx - box, cx + box + 1):
            if image.getpixel((x, y)) == color:
                return True
    return False
