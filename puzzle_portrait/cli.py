"""Command-line entry point for Puzzle Portrait."""

import argparse
import sys
from pathlib import Path

from puzzle_portrait.config import DEFAULT_OUTPUT_DIR
from puzzle_portrait.export import save_image
from puzzle_portrait.image import image_info, load_image, make_preview


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
        help="Crop and resize a photograph to a 100x100 preview image.",
    )
    preview_parser.add_argument("image", type=Path, help="Path to the input photograph")
    preview_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the preview image (default: output)",
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
    output_path = save_image(
        preview,
        args.output_dir / f"{args.image.stem}_preview.png",
    )
    print(output_path)
    return 0
