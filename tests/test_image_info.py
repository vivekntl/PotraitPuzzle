from PIL import Image

from puzzle_portrait.image import image_info


def test_image_info_reports_width_height_mode_and_aspect_ratio() -> None:
    image = Image.new("RGB", (16, 8), color=(12, 34, 56))

    info = image_info(image)

    assert info.width == 16
    assert info.height == 8
    assert info.mode == "RGB"
    assert info.aspect_ratio == 2.0


def test_image_info_reports_grayscale_mode() -> None:
    image = Image.new("L", (3, 4), color=128)

    info = image_info(image)

    assert info.width == 3
    assert info.height == 4
    assert info.mode == "L"
    assert info.aspect_ratio == 0.75


def test_image_info_does_not_modify_the_image() -> None:
    image = Image.new("RGB", (4, 2), color=(10, 20, 30))
    pixels_before = image.tobytes()

    image_info(image)

    assert image.size == (4, 2)
    assert image.mode == "RGB"
    assert image.tobytes() == pixels_before
