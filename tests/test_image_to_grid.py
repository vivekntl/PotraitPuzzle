from PIL import Image

from puzzle_portrait.grid import RGB
from puzzle_portrait.image import grid_from_image


def test_grid_from_image_matches_dimensions_and_pixel_colors() -> None:
    image = Image.new("RGB", (3, 2))
    image.putpixel((0, 0), (10, 20, 30))
    image.putpixel((1, 0), (40, 50, 60))
    image.putpixel((2, 0), (70, 80, 90))
    image.putpixel((0, 1), (100, 110, 120))
    image.putpixel((1, 1), (130, 140, 150))
    image.putpixel((2, 1), (160, 170, 180))

    grid = grid_from_image(image)

    assert grid.dimensions == image.size
    assert grid.width == 3
    assert grid.height == 2
    assert grid[0, 0].color == RGB(10, 20, 30)
    assert grid[0, 1].color == RGB(40, 50, 60)
    assert grid[0, 2].color == RGB(70, 80, 90)
    assert grid[1, 0].color == RGB(100, 110, 120)
    assert grid[1, 1].color == RGB(130, 140, 150)
    assert grid[1, 2].color == RGB(160, 170, 180)
    assert grid[0, 0].row == 0
    assert grid[0, 0].column == 0
    assert grid[1, 2].row == 1
    assert grid[1, 2].column == 2


def test_grid_from_image_converts_grayscale_to_rgb() -> None:
    image = Image.new("L", (2, 1), color=128)

    grid = grid_from_image(image)

    assert grid.dimensions == (2, 1)
    assert grid[0, 0].color == RGB(128, 128, 128)
    assert grid[0, 1].color == RGB(128, 128, 128)


def test_grid_from_image_does_not_modify_source() -> None:
    image = Image.new("RGB", (2, 2), color=(7, 8, 9))
    pixels_before = image.tobytes()

    grid_from_image(image)

    assert image.size == (2, 2)
    assert image.tobytes() == pixels_before
