"""Convert a processed image into a mosaic grid."""

from PIL.Image import Image as PILImage

from puzzle_portrait.grid import Grid, RGB


def grid_from_image(image: PILImage) -> Grid:
    """Build a grid where each pixel becomes a cell with that pixel's RGB color."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    grid = Grid(width, height)

    for row in range(height):
        for column in range(width):
            red, green, blue = pixels[column, row]
            grid[row, column] = RGB(red, green, blue)

    return grid
