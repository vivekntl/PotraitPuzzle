"""Read-only information about an input image."""

from dataclasses import dataclass

from PIL.Image import Image as PILImage


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int
    mode: str
    aspect_ratio: float


def image_info(image: PILImage) -> ImageInfo:
    """Return width, height, color mode, and aspect ratio without modifying ``image``."""
    width, height = image.size
    if height == 0:
        raise ValueError("Cannot compute aspect ratio for an image with height 0")

    return ImageInfo(
        width=width,
        height=height,
        mode=image.mode,
        aspect_ratio=width / height,
    )
