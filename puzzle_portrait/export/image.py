"""Save images to the filesystem."""

from pathlib import Path

from PIL.Image import Image as PILImage


def save_image(image: PILImage, path: str | Path) -> Path:
    """Write ``image`` to ``path``, creating parent directories as needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path
