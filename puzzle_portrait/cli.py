"""Command-line entry point for Puzzle Portrait."""

import argparse
import sys
from pathlib import Path

from puzzle_portrait.config import (
    COLOR_COUNTS,
    DEFAULT_CELL_SIZE,
    DEFAULT_COLOR_COUNT,
    DEFAULT_OUTPUT_DIR,
)
from puzzle_portrait.export import save_image
from puzzle_portrait.image import (
    grid_from_image,
    image_info,
    load_image,
    make_preview,
    quantize_colors,
)
from puzzle_portrait.render import render_color_grid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate word-search mosaics from portrait images.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser(
        "info",
        help="Print width, height, color mode, and aspect ratio.",
    )
    info_parser.add_argument("image", type=Path, help="Path to the input image")

    preview_parser = subparsers.add_parser(
        "preview",
        help="Crop, resize, and save full-color and quantized preview images.",
    )
    preview_parser.add_argument("image", type=Path, help="Path to the input photograph")
    preview_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the preview images (default: output)",
    )
    preview_parser.add_argument(
        "--colors",
        type=int,
        choices=COLOR_COUNTS,
        default=DEFAULT_COLOR_COUNT,
        help=f"Palette size for the quantized preview (default: {DEFAULT_COLOR_COUNT})",
    )

    render_parser = subparsers.add_parser(
        "render",
        help="Render a color-cell mosaic PNG from a photograph.",
    )
    render_parser.add_argument("image", type=Path, help="Path to the input photograph")
    render_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the mosaic PNG (default: output)",
    )
    render_parser.add_argument(
        "--colors",
        type=int,
        choices=COLOR_COUNTS,
        default=DEFAULT_COLOR_COUNT,
        help=f"Palette size (default: {DEFAULT_COLOR_COUNT})",
    )
    render_parser.add_argument(
        "--cell-size",
        type=int,
        default=DEFAULT_CELL_SIZE,
        help=f"Pixel size of each square cell (default: {DEFAULT_CELL_SIZE})",
    )
    render_parser.add_argument(
        "--grid-lines",
        action="store_true",
        help="Draw a subtle line between cells",
    )
    return parser


def _load_or_exit(path: Path):
    try:
        return load_image(path)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    image = _load_or_exit(args.image)
    if image is None:
        return 1

    if args.command == "info":
        info = image_info(image)
        print(f"width: {info.width}")
        print(f"height: {info.height}")
        print(f"mode: {info.mode}")
        print(f"aspect_ratio: {info.aspect_ratio}")
        return 0

    preview = make_preview(image)
    quantized = quantize_colors(preview, args.colors)

    if args.command == "preview":
        preview_path = save_image(
            preview,
            args.output_dir / f"{args.image.stem}_preview.png",
        )
        quantized_path = save_image(
            quantized,
            args.output_dir / f"{args.image.stem}_preview_{args.colors}colors.png",
        )
        print(preview_path)
        print(quantized_path)
        return 0

    mosaic = render_color_grid(
        grid_from_image(quantized),
        cell_size=args.cell_size,
        grid_lines=args.grid_lines,
    )
    mosaic_path = save_image(
        mosaic,
        args.output_dir / f"{args.image.stem}_mosaic.png",
    )
    print(mosaic_path)
    return 0
