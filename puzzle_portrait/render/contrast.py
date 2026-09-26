"""Choose a readable text color from a tile's background luminance."""

from puzzle_portrait.grid import RGB

LIGHT_TEXT = RGB(250, 250, 250)
DARK_TEXT = RGB(20, 20, 20)
LUMINANCE_THRESHOLD = 0.55


def relative_luminance(color: RGB) -> float:
    """Return Rec. 709 luminance of ``color`` in the range 0..1."""
    return (0.2126 * color.red + 0.7152 * color.green + 0.0722 * color.blue) / 255


def contrasting_text_color(
    background: RGB,
    *,
    light: RGB = LIGHT_TEXT,
    dark: RGB = DARK_TEXT,
    threshold: float = LUMINANCE_THRESHOLD,
) -> RGB:
    """Return ``dark`` text on light backgrounds and ``light`` text on dark ones."""
    if relative_luminance(background) >= threshold:
        return dark
    return light
