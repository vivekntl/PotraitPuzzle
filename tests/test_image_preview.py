from PIL import Image
from PIL.Image import Image as PILImage

from puzzle_portrait.image import make_preview, resize_to_grid


def _unique_image(width: int, height: int) -> PILImage:
    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), ((x * 3) % 256, (y * 5) % 256, (x + y) % 256))
    return image


def test_make_preview_is_100x100_square() -> None:
    source = _unique_image(16, 10)

    preview = make_preview(source)

    assert preview.size == (100, 100)


def test_make_preview_crops_then_resizes_like_grid() -> None:
    source = _unique_image(16, 10)

    preview = make_preview(source)

    assert preview.tobytes() == resize_to_grid(source, 100, 100).tobytes()


def test_make_preview_does_not_modify_source() -> None:
    source = _unique_image(16, 10)
    pixels_before = source.tobytes()

    make_preview(source)

    assert source.size == (16, 10)
    assert source.tobytes() == pixels_before
