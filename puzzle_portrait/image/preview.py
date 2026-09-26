"""Build a small square preview of a photograph."""

from PIL.Image import Image as PILImage

from puzzle_portrait.config import PREVIEW_SIZE
from puzzle_portrait.image.resize import resize_to_grid


def make_preview(image: PILImage, size: int = PREVIEW_SIZE) -> PILImage:
    """Crop to a centered square and resize to ``size`` x ``size``."""
    return resize_to_grid(image, size, size)
