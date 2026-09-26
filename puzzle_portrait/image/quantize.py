"""Reduce an image to a limited palette with Pillow quantization."""

from PIL import Image
from PIL.Image import Image as PILImage

from puzzle_portrait.config import COLOR_COUNTS


def quantize_colors(image: PILImage, colors: int) -> PILImage:
    """Return a new RGB image using at most ``colors`` palette entries.

    ``colors`` must be one of the configured counts: 8, 16, 24, 32, or 48.
    The source image is not modified.
    """
    if colors not in COLOR_COUNTS:
        allowed = ", ".join(str(count) for count in COLOR_COUNTS)
        raise ValueError(f"colors must be one of {allowed}, got {colors}")

    rgb = image.convert("RGB")
    quantized = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    return quantized.convert("RGB")
