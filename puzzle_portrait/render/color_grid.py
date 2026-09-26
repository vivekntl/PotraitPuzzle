"""Render a color grid as square cells, optionally with centered letters."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage
from PIL.ImageFont import FreeTypeFont, ImageFont as BitmapFont

from puzzle_portrait.config import (
    DEFAULT_CELL_SIZE,
    DEFAULT_FONT_SIZE,
    DEFAULT_FONT_WEIGHT,
)
from puzzle_portrait.grid import ColorGrid, RGB
from puzzle_portrait.render.contrast import (
    DARK_TEXT,
    LIGHT_TEXT,
    contrasting_text_color,
)

SUBTLE_GRID_LINE = RGB(48, 48, 48)
DEFAULT_TEXT_COLOR = DARK_TEXT

_BOLD_WEIGHTS = frozenset({"bold", "700", "800", "900"})

FontType = FreeTypeFont | BitmapFont


def render_color_grid(
    grid: ColorGrid,
    cell_size: int = DEFAULT_CELL_SIZE,
    *,
    grid_lines: bool = False,
    grid_line_color: RGB = SUBTLE_GRID_LINE,
    draw_letters: bool = True,
    font: str | Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
    font_weight: str = DEFAULT_FONT_WEIGHT,
    text_color: RGB = DEFAULT_TEXT_COLOR,
    auto_text_color: bool = True,
    light_text_color: RGB = LIGHT_TEXT,
    dark_text_color: RGB = DARK_TEXT,
) -> PILImage:
    """Return a PNG-ready image of colored square cells.

    When a cell has a letter and ``draw_letters`` is true, that letter is
    drawn in the cell center. By default the text is light or dark based on
    the tile luminance. Set ``auto_text_color=False`` to use ``text_color``
    for every tile.
    """
    if cell_size < 1:
        raise ValueError(f"cell_size must be at least 1, got {cell_size}")
    if font_size < 1:
        raise ValueError(f"font_size must be at least 1, got {font_size}")

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

    if draw_letters:
        _draw_letters(
            image,
            grid,
            cell_size,
            font,
            font_size,
            font_weight,
            text_color,
            auto_text_color,
            light_text_color,
            dark_text_color,
        )

    if grid_lines:
        _draw_grid_lines(image, grid, cell_size, grid_line_color)

    return image


def _draw_letters(
    image: PILImage,
    grid: ColorGrid,
    cell_size: int,
    font: str | Path | None,
    font_size: int,
    font_weight: str,
    text_color: RGB,
    auto_text_color: bool,
    light_text_color: RGB,
    dark_text_color: RGB,
) -> None:
    loaded = _load_font(font, font_size, font_weight)
    draw = ImageDraw.Draw(image)

    for row in range(grid.height):
        for column in range(grid.width):
            cell = grid[row, column]
            if not cell.character:
                continue
            if auto_text_color:
                chosen = contrasting_text_color(
                    cell.color,
                    light=light_text_color,
                    dark=dark_text_color,
                )
            else:
                chosen = text_color
            fill = (chosen.red, chosen.green, chosen.blue)
            cx = column * cell_size + cell_size / 2
            cy = row * cell_size + cell_size / 2
            draw.text((cx, cy), cell.character, font=loaded, fill=fill, anchor="mm")


def _load_font(
    font: str | Path | None,
    size: int,
    weight: str,
) -> FontType:
    if font is None:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    path = _resolve_font_path(Path(font), weight)
    if not path.is_file():
        raise FileNotFoundError(f"Font not found: {path}")
    return ImageFont.truetype(str(path), size=size)


def _resolve_font_path(path: Path, weight: str) -> Path:
    if weight.lower() not in _BOLD_WEIGHTS:
        return path

    candidates = (
        path.with_stem(f"{path.stem}bd"),
        path.with_stem(f"{path.stem}b"),
        path.with_stem(f"{path.stem}-Bold"),
        path.with_stem(f"{path.stem} Bold"),
        path.with_stem(f"{path.stem}_Bold"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return path


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
