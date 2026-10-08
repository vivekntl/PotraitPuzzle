"""Build a lettered mosaic preview off the UI thread."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from PIL.Image import Image as PILImage
from PySide6.QtCore import QThread, Signal

from puzzle_portrait.grid import RGB, combine_grids
from puzzle_portrait.image import crop_region, grid_from_image, quantize_colors, resize_to_grid
from puzzle_portrait.render import render_color_grid
from puzzle_portrait.wordsearch import (
    Direction,
    LetterGrid,
    WordSearch,
    fill_empty_random,
    generate_word_search,
)


@dataclass(frozen=True, slots=True)
class PreviewSettings:
    crop_x: int
    crop_y: int
    crop_width: int
    crop_height: int
    columns: int
    rows: int
    color_count: int
    words: tuple[str, ...]
    seed: int
    spread_words: bool
    spread_rate: float
    balance_directions: bool
    direction_weights: Mapping[Direction, float] | None
    directions: Sequence[Direction]
    fill_percent: int
    allow_phrases: bool
    tile_size: int
    font: str | None
    font_size: int
    font_weight: str
    text_color_mode: str
    text_color: RGB


@dataclass(frozen=True, slots=True)
class PreviewResult:
    image: PILImage
    failed_words: tuple[str, ...]


def render_preview(source_image: PILImage, settings: PreviewSettings) -> PreviewResult:
    """Crop, place letters, and render a lettered mosaic from a settings snapshot."""
    cropped = crop_region(
        source_image,
        settings.crop_x,
        settings.crop_y,
        settings.crop_width,
        settings.crop_height,
    )
    sampled = resize_to_grid(cropped, settings.columns, settings.rows)
    quantized = quantize_colors(sampled, settings.color_count)
    puzzle = _word_search(settings)
    combined = combine_grids(grid_from_image(quantized), puzzle.grid)
    style = {
        "font_weight": settings.font_weight,
        "text_color_mode": settings.text_color_mode,
        "text_color": settings.text_color,
    }
    try:
        image = render_color_grid(
            combined,
            cell_size=settings.tile_size,
            draw_letters=True,
            font=settings.font,
            font_size=settings.font_size,
            grid_lines=True,
            **style,
        )
    except (OSError, FileNotFoundError):
        image = render_color_grid(
            combined,
            cell_size=settings.tile_size,
            draw_letters=True,
            font_size=settings.font_size,
            grid_lines=True,
            **style,
        )
    return PreviewResult(image=image, failed_words=puzzle.failed_words)


def _word_search(settings: PreviewSettings) -> WordSearch:
    if settings.words:
        return generate_word_search(
            settings.columns,
            settings.rows,
            settings.words,
            directions=settings.directions,
            seed=settings.seed,
            spread_words=settings.spread_words,
            spread_rate=settings.spread_rate,
            balance_directions=settings.balance_directions,
            direction_weights=settings.direction_weights,
            fill_percent=settings.fill_percent,
            allow_phrases=settings.allow_phrases,
        )
    grid = LetterGrid(settings.columns, settings.rows)
    fill_empty_random(grid, seed=settings.seed, percent=settings.fill_percent)
    return WordSearch(grid=grid, placements=(), failed_words=())


class PreviewWorker(QThread):
    preview_ready = Signal(object, int, object)
    preview_failed = Signal(str, int)

    def __init__(
        self,
        request_id: int,
        source_image: PILImage,
        settings: PreviewSettings,
    ) -> None:
        super().__init__()
        self._request_id = request_id
        self._source_image = source_image
        self._settings = settings

    def run(self) -> None:
        try:
            result = render_preview(self._source_image, self._settings)
        except (OSError, ValueError) as exc:
            self.preview_failed.emit(str(exc), self._request_id)
            return
        self.preview_ready.emit(result.image, self._request_id, result.failed_words)
