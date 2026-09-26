import pytest
from PIL import Image
from PIL.Image import Image as PILImage

from puzzle_portrait.image import crop_to_aspect_ratio, resize_to_grid


def _unique_image(width: int, height: int) -> PILImage:
    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), ((x * 3) % 256, (y * 5) % 256, (x + y) % 256))
    return image


def _expected(source: PILImage, grid_width: int, grid_height: int) -> PILImage:
    cropped = crop_to_aspect_ratio(source, grid_width / grid_height)
    return cropped.resize((grid_width, grid_height), Image.Resampling.LANCZOS)


def test_resize_to_landscape_grid_crops_then_resizes() -> None:
    source = _unique_image(12, 12)
    result = resize_to_grid(source, 8, 4)

    assert result.size == (8, 4)
    assert result.tobytes() == _expected(source, 8, 4).tobytes()


def test_resize_to_portrait_grid_crops_then_resizes() -> None:
    source = _unique_image(12, 12)
    result = resize_to_grid(source, 4, 8)

    assert result.size == (4, 8)
    assert result.tobytes() == _expected(source, 4, 8).tobytes()


def test_resize_to_square_grid_crops_then_resizes() -> None:
    source = _unique_image(16, 10)
    result = resize_to_grid(source, 5, 5)

    assert result.size == (5, 5)
    assert result.tobytes() == _expected(source, 5, 5).tobytes()


def test_resize_to_grid_does_not_modify_source() -> None:
    source = _unique_image(16, 10)
    pixels_before = source.tobytes()

    resize_to_grid(source, 4, 4)

    assert source.size == (16, 10)
    assert source.tobytes() == pixels_before


def test_resize_to_grid_rejects_non_positive_size() -> None:
    source = _unique_image(8, 8)

    with pytest.raises(ValueError, match="1x1"):
        resize_to_grid(source, 0, 4)
