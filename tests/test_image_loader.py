from pathlib import Path

import pytest
from PIL.Image import Image as PILImage

from puzzle_portrait.image import load_image

FIXTURE = Path(__file__).parent / "fixtures" / "sample.png"


def test_load_image_returns_pillow_image() -> None:
    image = load_image(FIXTURE)

    assert isinstance(image, PILImage)
    assert image.size == (8, 8)
    assert image.format == "PNG"


def test_load_image_accepts_string_path() -> None:
    image = load_image(str(FIXTURE))

    assert isinstance(image, PILImage)
    assert image.size == (8, 8)


def test_load_image_missing_path_raises_clear_error(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.png"

    with pytest.raises(FileNotFoundError, match="Image not found"):
        load_image(missing)


def test_load_image_directory_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Image path is not a file"):
        load_image(tmp_path)
