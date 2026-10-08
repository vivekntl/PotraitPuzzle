"""Save and load a generation folder that can reproduce a mosaic."""

from __future__ import annotations

import json
import shutil
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL.Image import Image as PILImage

from puzzle_portrait.config import (
    CONFIG_FILENAME,
    DEFAULT_SEED,
    MOSAIC_FILENAME,
    MOSAIC_LETTERS_FILENAME,
    MOSAIC_LETTERS_SVG_FILENAME,
    MOSAIC_SVG_FILENAME,
    WORDS_FILENAME,
    mosaic_letters_svg_filename,
)
from puzzle_portrait.export import save_image, save_svg

CONFIG_VERSION = 1


@dataclass(frozen=True, slots=True)
class ProjectSettings:
    image: str
    words: tuple[str, ...]
    words_file: str
    seed: int
    color_count: int
    crop_x: int
    crop_y: int
    crop_width: int
    crop_height: int
    columns: int
    rows: int
    tile_size: int
    font: str
    font_file: str | None
    font_size: int
    grid_lines: bool
    mosaic: str
    mosaic_letters: str
    failed_words: tuple[str, ...] = ()
    mosaic_svg: str = MOSAIC_SVG_FILENAME
    mosaic_letters_svg: str = MOSAIC_LETTERS_SVG_FILENAME
    spread_words: bool = False
    spread_rate: float = 1.0
    balance_directions: bool = False
    horizontal_weight: float = 1.0
    vertical_weight: float = 1.0
    diagonal_weight: float = 1.0
    font_weight: str = "regular"
    text_color_mode: str = "automatic"
    custom_text_color: tuple[int, int, int] = (20, 20, 20)
    allow_phrases: bool = True
    fill_percent: int = 100
    allow_backwards: bool = True


def project_config_path(directory: str | Path) -> Path:
    path = Path(directory)
    if path.is_file():
        return path
    return path / CONFIG_FILENAME


def save_project(
    directory: str | Path,
    settings: ProjectSettings,
    *,
    source_image: str | Path,
    mosaic: PILImage,
    mosaic_letters: PILImage,
    mosaic_svg: str | None = None,
    mosaic_letters_svg: str | None = None,
    mosaic_letters_svgs: Mapping[str, str] | None = None,
) -> Path:
    """Write config, words, a copy of the input, PNG mosaics, and SVG prints."""
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_name = _copy_input_image(source_image, output_dir)
    words_path = output_dir / WORDS_FILENAME
    words_path.write_text(
        "\n".join(settings.words) + ("\n" if settings.words else ""),
        encoding="utf-8",
    )
    save_image(mosaic, output_dir / MOSAIC_FILENAME)
    save_image(mosaic_letters, output_dir / MOSAIC_LETTERS_FILENAME)
    svg_name = None
    letters_svg_name = None
    if mosaic_svg is not None:
        save_svg(mosaic_svg, output_dir / MOSAIC_SVG_FILENAME)
        svg_name = MOSAIC_SVG_FILENAME
    if mosaic_letters_svg is not None:
        save_svg(mosaic_letters_svg, output_dir / MOSAIC_LETTERS_SVG_FILENAME)
        letters_svg_name = MOSAIC_LETTERS_SVG_FILENAME
    weight_svg_names: dict[str, str] = {}
    if mosaic_letters_svgs:
        for weight, svg in mosaic_letters_svgs.items():
            name = mosaic_letters_svg_filename(weight)
            save_svg(svg, output_dir / name)
            weight_svg_names[weight] = name

    payload = _settings_to_payload(
        settings,
        image=image_name,
        words_file=WORDS_FILENAME,
        mosaic=MOSAIC_FILENAME,
        mosaic_letters=MOSAIC_LETTERS_FILENAME,
        mosaic_svg=svg_name,
        mosaic_letters_svg=letters_svg_name,
        mosaic_letters_svgs=weight_svg_names or None,
    )
    config_path = output_dir / CONFIG_FILENAME
    config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return config_path


def load_project(path: str | Path) -> tuple[ProjectSettings, Path]:
    """Read a project folder or config file. Paths are resolved from the folder."""
    config_path = project_config_path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Project config not found: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Project config must be a JSON object")

    folder = config_path.parent
    settings = settings_from_dict(data)
    words = _words_from_folder(folder, settings)
    settings = ProjectSettings(
        **{**asdict(settings), "words": words},
    )
    return settings, folder


def settings_from_dict(data: dict[str, Any]) -> ProjectSettings:
    crop = data.get("crop") if isinstance(data.get("crop"), dict) else {}
    outputs = data.get("outputs") if isinstance(data.get("outputs"), dict) else {}
    words = data.get("words") or []
    if not isinstance(words, list):
        raise ValueError("words must be a list of strings")

    font_file = data.get("font_file")
    weights = (
        data.get("direction_weights")
        if isinstance(data.get("direction_weights"), dict)
        else {}
    )
    return ProjectSettings(
        image=str(data.get("image") or ""),
        words=tuple(str(word) for word in words if str(word).strip()),
        words_file=str(data.get("words_file") or WORDS_FILENAME),
        seed=int(data.get("seed", DEFAULT_SEED)),
        color_count=int(data.get("color_count")),
        crop_x=int(crop.get("x", 0)),
        crop_y=int(crop.get("y", 0)),
        crop_width=int(crop.get("width")),
        crop_height=int(crop.get("height")),
        columns=int(data.get("columns")),
        rows=int(data.get("rows")),
        tile_size=int(data.get("tile_size")),
        font=str(data.get("font") or ""),
        font_file=str(font_file) if font_file else None,
        font_size=int(data.get("font_size")),
        grid_lines=bool(data.get("grid_lines", True)),
        mosaic=str(outputs.get("mosaic") or MOSAIC_FILENAME),
        mosaic_letters=str(outputs.get("mosaic_letters") or MOSAIC_LETTERS_FILENAME),
        failed_words=tuple(str(word) for word in data.get("failed_words") or ()),
        mosaic_svg=str(outputs.get("mosaic_svg") or MOSAIC_SVG_FILENAME),
        mosaic_letters_svg=str(
            outputs.get("mosaic_letters_svg") or MOSAIC_LETTERS_SVG_FILENAME
        ),
        spread_words=bool(data["spread_words"]) if "spread_words" in data else False,
        spread_rate=float(data["spread_rate"]) if "spread_rate" in data else 1.0,
        balance_directions=bool(data.get("balance_directions", False)),
        horizontal_weight=float(weights.get("horizontal", 1.0)),
        vertical_weight=float(weights.get("vertical", 1.0)),
        diagonal_weight=float(weights.get("diagonal", 1.0)),
        font_weight=str(data.get("font_weight") or "regular"),
        text_color_mode=str(data.get("text_color_mode") or "automatic"),
        custom_text_color=_rgb_tuple(data.get("custom_text_color"), (20, 20, 20)),
        allow_phrases=bool(data["allow_phrases"]) if "allow_phrases" in data else True,
        fill_percent=_fill_percent_from_dict(data),
        allow_backwards=(
            bool(data["allow_backwards"]) if "allow_backwards" in data else True
        ),
    )


def _fill_percent_from_dict(data: dict[str, Any]) -> int:
    if "fill_percent" in data:
        percent = int(data["fill_percent"])
    elif "fill_empty" in data:
        percent = 100 if data["fill_empty"] else 0
    else:
        percent = 100
    return max(0, min(100, percent))


def _rgb_tuple(value: Any, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return default
    return (int(value[0]), int(value[1]), int(value[2]))


def resolve_project_file(folder: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute():
        return path
    return folder / path


def _copy_input_image(source_image: str | Path, output_dir: Path) -> str:
    source = Path(source_image)
    if source.is_file():
        name = f"input{source.suffix.lower() or '.png'}"
        destination = output_dir / name
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        return name
    raise FileNotFoundError(f"Input image not found: {source}")


def _settings_to_payload(
    settings: ProjectSettings,
    *,
    image: str,
    words_file: str,
    mosaic: str,
    mosaic_letters: str,
    mosaic_svg: str | None,
    mosaic_letters_svg: str | None,
    mosaic_letters_svgs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "version": CONFIG_VERSION,
        "image": image,
        "words_file": words_file,
        "words": list(settings.words),
        "seed": settings.seed,
        "color_count": settings.color_count,
        "crop": {
            "x": settings.crop_x,
            "y": settings.crop_y,
            "width": settings.crop_width,
            "height": settings.crop_height,
        },
        "columns": settings.columns,
        "rows": settings.rows,
        "tile_size": settings.tile_size,
        "font": settings.font,
        "font_file": settings.font_file,
        "font_size": settings.font_size,
        "font_weight": settings.font_weight,
        "text_color_mode": settings.text_color_mode,
        "custom_text_color": list(settings.custom_text_color),
        "grid_lines": settings.grid_lines,
        "spread_words": settings.spread_words,
        "spread_rate": settings.spread_rate,
        "balance_directions": settings.balance_directions,
        "allow_phrases": settings.allow_phrases,
        "fill_percent": settings.fill_percent,
        "allow_backwards": settings.allow_backwards,
        "direction_weights": {
            "horizontal": settings.horizontal_weight,
            "vertical": settings.vertical_weight,
            "diagonal": settings.diagonal_weight,
        },
        "failed_words": list(settings.failed_words),
        "outputs": {
            "mosaic": mosaic,
            "mosaic_letters": mosaic_letters,
            **({"mosaic_svg": mosaic_svg} if mosaic_svg else {}),
            **({"mosaic_letters_svg": mosaic_letters_svg} if mosaic_letters_svg else {}),
            **(
                {"mosaic_letters_svgs": dict(mosaic_letters_svgs)}
                if mosaic_letters_svgs
                else {}
            ),
        },
    }


def _words_from_folder(folder: Path, settings: ProjectSettings) -> tuple[str, ...]:
    words_path = resolve_project_file(folder, settings.words_file)
    if words_path.is_file():
        text = words_path.read_text(encoding="utf-8")
        words = tuple(line.strip() for line in text.splitlines() if line.strip())
        if words:
            return words
    return settings.words
