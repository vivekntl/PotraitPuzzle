"""Command-line entry point for Puzzle Portrait."""

import argparse
import sys
from pathlib import Path

from puzzle_portrait.config import (
    COLOR_COUNTS,
    DEFAULT_ALLOW_BACKWARDS,
    DEFAULT_ALLOW_PHRASES,
    DEFAULT_BALANCE_DIRECTIONS,
    DEFAULT_CELL_SIZE,
    DEFAULT_COLOR_COUNT,
    DEFAULT_DIAGONAL_WEIGHT,
    DEFAULT_FILL_EMPTY,
    DEFAULT_FONT_SIZE,
    DEFAULT_HORIZONTAL_WEIGHT,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SPREAD_RATE,
    DEFAULT_SPREAD_WORDS,
    DEFAULT_VERTICAL_WEIGHT,
    mosaic_letters_svg_filename,
)
from puzzle_portrait.export import save_image, save_svg
from puzzle_portrait.grid import combine_grids
from puzzle_portrait.image import (
    grid_from_image,
    image_info,
    load_image,
    make_preview,
    quantize_colors,
)
from puzzle_portrait.render import (
    available_font_weights,
    render_color_grid,
    render_color_grid_svg,
)
from puzzle_portrait.wordsearch import (
    direction_weights_from_axes,
    generate_word_search,
    placement_directions,
)


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

    mosaic_parser = subparsers.add_parser(
        "mosaic",
        help="Build a color mosaic and a letter mosaic from a photo and word list.",
    )
    mosaic_parser.add_argument("image", type=Path, help="Path to the input photograph")
    mosaic_parser.add_argument(
        "words",
        nargs="+",
        help="Words to place in the word-search",
    )
    mosaic_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the mosaic PNGs (default: output)",
    )
    mosaic_parser.add_argument(
        "--colors",
        type=int,
        choices=COLOR_COUNTS,
        default=DEFAULT_COLOR_COUNT,
        help=f"Palette size (default: {DEFAULT_COLOR_COUNT})",
    )
    mosaic_parser.add_argument(
        "--cell-size",
        type=int,
        default=DEFAULT_CELL_SIZE,
        help=f"Pixel size of each square cell (default: {DEFAULT_CELL_SIZE})",
    )
    mosaic_parser.add_argument(
        "--grid-lines",
        action="store_true",
        help="Draw a subtle line between cells",
    )
    mosaic_parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for word placement and filler (default: 42)",
    )
    mosaic_parser.add_argument(
        "--font-size",
        type=int,
        default=DEFAULT_FONT_SIZE,
        help=f"Letter size in pixels (default: {DEFAULT_FONT_SIZE})",
    )
    mosaic_parser.add_argument(
        "--spread-words",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_SPREAD_WORDS,
        help="Place early words near the center and later words farther out (default: on)",
    )
    mosaic_parser.add_argument(
        "--spread-rate",
        type=float,
        default=DEFAULT_SPREAD_RATE,
        help="How quickly later words move away from the center (default: 1)",
    )
    mosaic_parser.add_argument(
        "--balance-directions",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_BALANCE_DIRECTIONS,
        help="Discourage packing most words on the same axis (default: off)",
    )
    mosaic_parser.add_argument(
        "--horizontal-weight",
        type=float,
        default=DEFAULT_HORIZONTAL_WEIGHT,
        help="Relative weight for left/right words (default: 1)",
    )
    mosaic_parser.add_argument(
        "--vertical-weight",
        type=float,
        default=DEFAULT_VERTICAL_WEIGHT,
        help="Relative weight for up/down words (default: 1)",
    )
    mosaic_parser.add_argument(
        "--diagonal-weight",
        type=float,
        default=DEFAULT_DIAGONAL_WEIGHT,
        help="Relative weight for diagonal words (default: 1)",
    )
    mosaic_parser.add_argument(
        "--allow-phrases",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_ALLOW_PHRASES,
        help="Place a quoted phrase such as 'someone cool' as one entry (default: off)",
    )
    mosaic_parser.add_argument(
        "--fill-empty",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_FILL_EMPTY,
        help="Fill leftover tiles with random letters (default: on)",
    )
    mosaic_parser.add_argument(
        "--allow-backwards",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_ALLOW_BACKWARDS,
        help="Also place words right-to-left and bottom-to-top (default: off)",
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

    if args.command == "render":
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

    color_grid = grid_from_image(quantized)
    words = [word.upper() for word in args.words]
    weights = direction_weights_from_axes(
        args.horizontal_weight,
        args.vertical_weight,
        args.diagonal_weight,
    )
    puzzle = generate_word_search(
        color_grid.width,
        color_grid.height,
        words,
        directions=placement_directions(allow_backwards=args.allow_backwards),
        seed=args.seed,
        spread_words=args.spread_words,
        spread_rate=args.spread_rate,
        balance_directions=args.balance_directions,
        direction_weights=weights,
        fill_empty=args.fill_empty,
        allow_phrases=args.allow_phrases,
    )
    if puzzle.failed_words:
        print("Failed to place: " + ", ".join(puzzle.failed_words), file=sys.stderr)

    combined = combine_grids(color_grid, puzzle.grid)
    plain = render_color_grid(
        combined,
        cell_size=args.cell_size,
        grid_lines=args.grid_lines,
        draw_letters=False,
    )
    lettered = render_color_grid(
        combined,
        cell_size=args.cell_size,
        grid_lines=args.grid_lines,
        draw_letters=True,
        font_size=args.font_size,
    )
    plain_path = save_image(
        plain,
        args.output_dir / f"{args.image.stem}_mosaic.png",
    )
    lettered_path = save_image(
        lettered,
        args.output_dir / f"{args.image.stem}_mosaic_letters.png",
    )
    plain_svg_path = save_svg(
        render_color_grid_svg(
            combined,
            cell_size=args.cell_size,
            grid_lines=args.grid_lines,
            draw_letters=False,
        ),
        args.output_dir / f"{args.image.stem}_mosaic.svg",
    )
    lettered_svg_path = save_svg(
        render_color_grid_svg(
            combined,
            cell_size=args.cell_size,
            grid_lines=args.grid_lines,
            draw_letters=True,
            font_size=args.font_size,
        ),
        args.output_dir / f"{args.image.stem}_mosaic_letters.svg",
    )
    print(plain_path)
    print(lettered_path)
    print(plain_svg_path)
    print(lettered_svg_path)
    for weight in available_font_weights(None):
        weight_path = save_svg(
            render_color_grid_svg(
                combined,
                cell_size=args.cell_size,
                grid_lines=args.grid_lines,
                draw_letters=True,
                font_size=args.font_size,
                font_weight=weight,
            ),
            args.output_dir
            / f"{args.image.stem}_{mosaic_letters_svg_filename(weight)}",
        )
        print(weight_path)
    return 0
