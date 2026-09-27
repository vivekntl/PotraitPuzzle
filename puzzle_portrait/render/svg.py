"""Render a color grid as a scalable SVG for print."""

from __future__ import annotations

import base64
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from puzzle_portrait.config import DEFAULT_CELL_SIZE, DEFAULT_FONT_SIZE, DEFAULT_FONT_WEIGHT
from puzzle_portrait.grid import ColorGrid, RGB
from puzzle_portrait.render.color_grid import (
    DEFAULT_TEXT_COLOR,
    SUBTLE_GRID_LINE,
    resolve_font_path,
)
from puzzle_portrait.render.contrast import (
    DARK_TEXT,
    LIGHT_TEXT,
    resolve_text_color_mode,
    text_color_for_tile,
)

_SVG_WEIGHTS = {
    "regular": "400",
    "normal": "400",
    "medium": "500",
    "semibold": "600",
    "bold": "700",
}

_EMBED_SUFFIXES = {".ttf": "truetype", ".otf": "opentype"}


def render_color_grid_svg(
    grid: ColorGrid,
    cell_size: int = DEFAULT_CELL_SIZE,
    *,
    grid_lines: bool = False,
    grid_line_color: RGB = SUBTLE_GRID_LINE,
    draw_letters: bool = True,
    font: str | Path | None = None,
    font_family: str | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
    font_weight: str = DEFAULT_FONT_WEIGHT,
    text_color: RGB = DEFAULT_TEXT_COLOR,
    auto_text_color: bool = True,
    text_color_mode: str | None = None,
    light_text_color: RGB = LIGHT_TEXT,
    dark_text_color: RGB = DARK_TEXT,
) -> str:
    """Return an SVG of colored square cells that can be printed at any size."""
    if cell_size < 1:
        raise ValueError(f"cell_size must be at least 1, got {cell_size}")
    if font_size < 1:
        raise ValueError(f"font_size must be at least 1, got {font_size}")

    width = grid.width * cell_size
    height = grid.height * cell_size
    family = font_family or "sans-serif"
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" '
            'preserveAspectRatio="xMidYMid meet">'
        ),
        "<!-- Puzzle Portrait mosaic. Scale freely for print. -->",
    ]

    embed_font = font
    if font is not None:
        embed_font = resolve_font_path(Path(font), font_weight)
    face = _embedded_font_face(embed_font) if draw_letters else ""
    if face:
        family = "PuzzlePortrait"
        parts.append(f"<defs><style>{face}</style></defs>")

    parts.extend(_cell_rects(grid, cell_size))
    if draw_letters:
        parts.extend(
            _letter_texts(
                grid,
                cell_size,
                family,
                font_size,
                font_weight,
                text_color,
                resolve_text_color_mode(text_color_mode, auto_text_color),
                light_text_color,
                dark_text_color,
            )
        )
    if grid_lines:
        parts.extend(_grid_lines(grid, cell_size, grid_line_color))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _cell_rects(grid: ColorGrid, cell_size: int) -> list[str]:
    by_color: dict[RGB, list[tuple[int, int]]] = defaultdict(list)
    for row in range(grid.height):
        for column in range(grid.width):
            by_color[grid[row, column].color].append((column, row))

    parts: list[str] = ['<g id="cells">']
    for color, cells in by_color.items():
        parts.append(f'<g fill="{_hex(color)}">')
        for column, row in cells:
            parts.append(
                f'<rect x="{column * cell_size}" y="{row * cell_size}" '
                f'width="{cell_size}" height="{cell_size}"/>'
            )
        parts.append("</g>")
    parts.append("</g>")
    return parts


def _letter_texts(
    grid: ColorGrid,
    cell_size: int,
    family: str,
    font_size: int,
    font_weight: str,
    text_color: RGB,
    text_color_mode: str,
    light_text_color: RGB,
    dark_text_color: RGB,
) -> list[str]:
    css_weight = _SVG_WEIGHTS.get(font_weight.lower(), "400")
    parts = [
        (
            f'<g id="letters" font-family="{_attr(family)}" '
            f'font-size="{font_size}" font-weight="{css_weight}" '
            'text-anchor="middle" dominant-baseline="central">'
        )
    ]
    for row in range(grid.height):
        for column in range(grid.width):
            cell = grid[row, column]
            if not cell.character:
                continue
            chosen = text_color_for_tile(
                cell.color,
                text_color_mode,
                custom=text_color,
                light=light_text_color,
                dark=dark_text_color,
            )
            cx = column * cell_size + cell_size / 2
            cy = row * cell_size + cell_size / 2
            parts.append(
                f'<text x="{_number(cx)}" y="{_number(cy)}" fill="{_hex(chosen)}">'
                f"{_xml_escape(cell.character)}</text>"
            )
    parts.append("</g>")
    return parts


def _grid_lines(grid: ColorGrid, cell_size: int, color: RGB) -> list[str]:
    width = grid.width * cell_size
    height = grid.height * cell_size
    stroke = _hex(color)
    parts = [f'<g id="grid" fill="none" stroke="{stroke}" stroke-width="1">']
    for column in range(1, grid.width):
        x = column * cell_size
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}"/>')
    for row in range(1, grid.height):
        y = row * cell_size
        parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}"/>')
    parts.append("</g>")
    return parts


def _embedded_font_face(font: str | Path | None) -> str:
    if font is None:
        return ""
    path = Path(font)
    fmt = _EMBED_SUFFIXES.get(path.suffix.lower())
    if fmt is None or not path.is_file():
        return ""
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:'PuzzlePortrait';"
        f"src:url(data:font/{fmt};base64,{data}) format('{fmt}');}}"
    )


def _attr(value: str) -> str:
    return _xml_escape(value, {'"': "&quot;", "'": "&apos;"})


def _hex(color: RGB) -> str:
    return f"#{color.red:02x}{color.green:02x}{color.blue:02x}"


def _number(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:g}"
