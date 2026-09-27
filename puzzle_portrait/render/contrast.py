"""Choose a readable text color from a tile's background luminance."""

from puzzle_portrait.grid import RGB

LIGHT_TEXT = RGB(250, 250, 250)
DARK_TEXT = RGB(20, 20, 20)
BLACK_TEXT = RGB(0, 0, 0)
WHITE_TEXT = RGB(255, 255, 255)
LUMINANCE_THRESHOLD = 0.55
TILE_SHADE_AMOUNT = 0.5

TEXT_MODE_AUTOMATIC = "automatic"
TEXT_MODE_BLACK = "black"
TEXT_MODE_WHITE = "white"
TEXT_MODE_CUSTOM = "custom"
TEXT_MODE_TILE_SHADE = "tile_shade"


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


def tile_shade_text_color(
    background: RGB,
    *,
    amount: float = TILE_SHADE_AMOUNT,
    threshold: float = LUMINANCE_THRESHOLD,
) -> RGB:
    """Return a lighter tint on dark tiles and a darker shade on light tiles."""
    amount = min(1.0, max(0.0, amount))
    if relative_luminance(background) >= threshold:
        return RGB(
            max(0, round(background.red * (1.0 - amount))),
            max(0, round(background.green * (1.0 - amount))),
            max(0, round(background.blue * (1.0 - amount))),
        )
    return RGB(
        min(255, round(background.red + (255 - background.red) * amount)),
        min(255, round(background.green + (255 - background.green) * amount)),
        min(255, round(background.blue + (255 - background.blue) * amount)),
    )


def resolve_text_color_mode(
    text_color_mode: str | None,
    auto_text_color: bool,
) -> str:
    """Use an explicit mode, or map the older ``auto_text_color`` flag."""
    if text_color_mode:
        return text_color_mode
    return TEXT_MODE_AUTOMATIC if auto_text_color else TEXT_MODE_CUSTOM


def text_color_for_tile(
    background: RGB,
    mode: str = TEXT_MODE_AUTOMATIC,
    *,
    custom: RGB = DARK_TEXT,
    light: RGB = LIGHT_TEXT,
    dark: RGB = DARK_TEXT,
) -> RGB:
    """Pick a letter color for ``background`` using ``mode``."""
    if mode == TEXT_MODE_BLACK:
        return BLACK_TEXT
    if mode == TEXT_MODE_WHITE:
        return WHITE_TEXT
    if mode == TEXT_MODE_CUSTOM:
        return custom
    if mode == TEXT_MODE_TILE_SHADE:
        return tile_shade_text_color(background)
    return contrasting_text_color(background, light=light, dark=dark)
