"""Centered crops that change aspect ratio without resizing."""

from PIL.Image import Image as PILImage


def crop_to_aspect_ratio(image: PILImage, aspect_ratio: float) -> PILImage:
    """Crop ``image`` to ``aspect_ratio`` (width / height), keeping the crop centered.

    The result is a new image. Pixel dimensions are only reduced, never scaled.
    """
    if aspect_ratio <= 0:
        raise ValueError(f"aspect_ratio must be positive, got {aspect_ratio}")

    width, height = image.size
    target_height = width / aspect_ratio

    if target_height <= height:
        new_width = width
        new_height = min(height, max(1, round(target_height)))
    else:
        new_width = min(width, max(1, round(height * aspect_ratio)))
        new_height = height

    left = (width - new_width) // 2
    top = (height - new_height) // 2
    return image.crop((left, top, left + new_width, top + new_height))
