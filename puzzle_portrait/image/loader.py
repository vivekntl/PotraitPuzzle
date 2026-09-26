"""Load images from the filesystem."""

from pathlib import Path

from PIL import Image
from PIL.Image import Image as PILImage


def load_image(path: str | Path) -> PILImage:
    """Load an image from ``path`` and return a Pillow ``Image``.

    Raises:
        FileNotFoundError: If ``path`` does not exist or is not a file.
    """
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    if not image_path.is_file():
        raise FileNotFoundError(f"Image path is not a file: {image_path}")

    image = Image.open(image_path)
    image.load()
    return image
