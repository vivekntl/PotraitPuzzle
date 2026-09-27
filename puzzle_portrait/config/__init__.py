"""Configuration and default settings for puzzle generation."""

from pathlib import Path

PREVIEW_SIZE = 100
DEFAULT_OUTPUT_DIR = Path("output")
COLOR_COUNTS = (8, 16, 24, 32, 48)
DEFAULT_COLOR_COUNT = 16
DEFAULT_CELL_SIZE = 8
MIN_TILE_SIZE = 2
MAX_TILE_SIZE = 32
DEFAULT_GRID_COLUMNS = 24
DEFAULT_GRID_ROWS = 24
MAX_GRID_SIZE = 100
DEFAULT_FONT_SIZE = 12
MIN_FONT_SIZE = 4
MAX_FONT_SIZE = 48
DEFAULT_FONT_WEIGHT = "regular"
FONT_WEIGHTS = ("regular", "medium", "semibold", "bold")
FONT_WEIGHT_LABELS = {
    "regular": "Regular",
    "medium": "Medium",
    "semibold": "SemiBold",
    "bold": "Bold",
}
DEFAULT_AUTO_TEXT_COLOR = True
DEFAULT_TEXT_COLOR_MODE = "automatic"
TEXT_COLOR_MODES = ("automatic", "black", "white", "custom", "tile_shade")
TEXT_COLOR_MODE_LABELS = {
    "automatic": "Automatic",
    "black": "Black",
    "white": "White",
    "custom": "Custom",
    "tile_shade": "Tile shade",
}
DEFAULT_SEED = 42
DEFAULT_SPREAD_WORDS = True
DEFAULT_SPREAD_RATE = 1.0
MIN_SPREAD_RATE = 0.0
MAX_SPREAD_RATE = 5.0
DEFAULT_BALANCE_DIRECTIONS = False
DEFAULT_ALLOW_PHRASES = False
DEFAULT_FILL_EMPTY = True
DEFAULT_ALLOW_BACKWARDS = False
DEFAULT_HORIZONTAL_WEIGHT = 1.0
DEFAULT_VERTICAL_WEIGHT = 1.0
DEFAULT_DIAGONAL_WEIGHT = 1.0
PREVIEW_DEBOUNCE_MS = 400
HELP_HOVER_DELAY_MS = 700
CONFIG_FILENAME = "puzzle-portrait.json"
WORDS_FILENAME = "words.txt"
MOSAIC_FILENAME = "mosaic.png"
MOSAIC_LETTERS_FILENAME = "mosaic_letters.png"
MOSAIC_SVG_FILENAME = "mosaic.svg"
MOSAIC_LETTERS_SVG_FILENAME = "mosaic_letters.svg"


def mosaic_letters_svg_filename(weight: str) -> str:
    """Return the lettered SVG filename for a font weight."""
    return f"mosaic_letters_{weight}.svg"
