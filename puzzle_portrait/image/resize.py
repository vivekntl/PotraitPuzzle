"""Resize images to a letter-grid size after a centered aspect crop."""

from PIL import Image
from PIL.Image import Image as PILImage

from puzzle_portrait.image.crop import crop_to_aspect_ratio


def resize_to_grid(image: PILImage, grid_width: int, grid_height: int) -> PILImage:
    """Crop to the grid aspect ratio, then resize to ``grid_width`` x ``grid_height``.

    Uses LANCZOS resampling for photographic preprocessing. The source image
    is not modified.
    """
    if grid_width < 1 or grid_height < 1:
        raise ValueError(
            f"Grid size must be at least 1x1, got {grid_width}x{grid_height}"
        )

    cropped = crop_to_aspect_ratio(image, grid_width / grid_height)
    return cropped.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
