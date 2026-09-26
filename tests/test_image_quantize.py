import pytest
from PIL import Image
from PIL.Image import Image as PILImage

from puzzle_portrait.config import COLOR_COUNTS
from puzzle_portrait.image import quantize_colors


def _colorful_image(width: int = 32, height: int = 32) -> PILImage:
    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), ((x * 7) % 256, (y * 11) % 256, (x * y) % 256))
    return image


def _unique_color_count(image: PILImage) -> int:
    colors = image.convert("RGB").getcolors(maxcolors=image.size[0] * image.size[1])
    assert colors is not None
    return len(colors)


@pytest.mark.parametrize("colors", COLOR_COUNTS)
def test_quantize_colors_reduces_palette(colors: int) -> None:
    source = _colorful_image()
    assert _unique_color_count(source) > colors

    quantized = quantize_colors(source, colors)

    assert quantized.size == source.size
    assert quantized.mode == "RGB"
    assert _unique_color_count(quantized) <= colors


def test_quantize_colors_does_not_modify_source() -> None:
    source = _colorful_image()
    pixels_before = source.tobytes()

    quantize_colors(source, 8)

    assert source.size == (32, 32)
    assert source.tobytes() == pixels_before


def test_quantize_colors_rejects_unsupported_count() -> None:
    source = _colorful_image()

    with pytest.raises(ValueError, match="colors must be one of"):
        quantize_colors(source, 12)
