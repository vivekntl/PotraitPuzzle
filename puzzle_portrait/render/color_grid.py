"""Render a color grid as square cells, without letters."""

from PIL import Image, ImageDraw
from PIL.Image import Image as PILImage

from puzzle_portrait.config import DEFAULT_CELL_SIZE
from puzzle_portrait.grid import ColorGrid, RGB

SUBTLE_GRID_LINE = RGB(48, 48, 48)


def render_color_grid(
    grid: ColorGrid,
    cell_size: int = DEFAULT_CELL_SIZE,
    *,
    grid_lines: bool = False,
    grid_line_color: RGB = SUBTLE_GRID_LINE,
) -> PILImage:
    """Return a PNG-ready image of colored square cells.

    ``cell_size`` is the width and height of each cell in pixels.
    When ``grid_lines`` is true, a 1-pixel line is drawn between cells.
    """
    if cell_size < 1:
        raise ValueError(f"cell_size must be at least 1, got {cell_size}")

    image = Image.new(
        "RGB",
        (grid.width * cell_size, grid.height * cell_size),
    )

    for row in range(grid.height):
        for column in range(grid.width):
            cell = grid[row, column]
            swatch = Image.new(
                "RGB",
                (cell_size, cell_size),
                (cell.color.red, cell.color.green, cell.color.blue),
            )
            image.paste(swatch, (column * cell_size, row * cell_size))

    if grid_lines:
        _draw_grid_lines(image, grid, cell_size, grid_line_color)

    return image


def _draw_grid_lines(
    image: PILImage,
    grid: ColorGrid,
    cell_size: int,
    color: RGB,
) -> None:
    draw = ImageDraw.Draw(image)
    line = (color.red, color.green, color.blue)
    width_px, height_px = image.size

    for column in range(1, grid.width):
        x = column * cell_size
        draw.line([(x, 0), (x, height_px - 1)], fill=line)

    for row in range(1, grid.height):
        y = row * cell_size
        draw.line([(0, y), (width_px - 1, y)], fill=line)
