import pytest
from PIL import Image

from puzzle_portrait.image import crop_region, crop_to_aspect_ratio


def _unique_image(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), ((x * 3) % 256, (y * 5) % 256, (x + y) % 256))
    return image


def test_crop_to_landscape_target_ratio() -> None:
    source = _unique_image(10, 10)

    cropped = crop_to_aspect_ratio(source, 2.0)

    assert cropped.size == (10, 5)
    assert cropped.tobytes() == source.crop((0, 2, 10, 7)).tobytes()


def test_crop_to_portrait_target_ratio() -> None:
    source = _unique_image(10, 10)

    cropped = crop_to_aspect_ratio(source, 0.5)

    assert cropped.size == (5, 10)
    assert cropped.tobytes() == source.crop((2, 0, 7, 10)).tobytes()


def test_crop_to_square_target_ratio() -> None:
    source = _unique_image(12, 8)

    cropped = crop_to_aspect_ratio(source, 1.0)

    assert cropped.size == (8, 8)
    assert cropped.tobytes() == source.crop((2, 0, 10, 8)).tobytes()


def test_crop_does_not_modify_source_or_resize() -> None:
    source = _unique_image(12, 8)
    pixels_before = source.tobytes()

    cropped = crop_to_aspect_ratio(source, 1.0)

    assert source.size == (12, 8)
    assert source.tobytes() == pixels_before
    assert cropped.size[0] <= 12
    assert cropped.size[1] <= 8
    assert cropped.size != source.size


def test_crop_region_returns_requested_box() -> None:
    source = _unique_image(10, 8)
    cropped = crop_region(source, 2, 1, 4, 3)

    assert cropped.size == (4, 3)
    assert cropped.tobytes() == source.crop((2, 1, 6, 4)).tobytes()
    assert source.size == (10, 8)


def test_crop_region_rejects_box_outside_image() -> None:
    source = _unique_image(6, 6)

    with pytest.raises(ValueError, match="outside"):
        crop_region(source, 4, 0, 4, 2)
