from pathlib import Path

from PIL import Image

from puzzle_portrait.export import save_image


def test_save_image_writes_file_and_creates_directory(tmp_path: Path) -> None:
    image = Image.new("RGB", (4, 4), color=(20, 40, 60))
    destination = tmp_path / "nested" / "preview.png"

    saved = save_image(image, destination)

    assert saved == destination
    assert destination.is_file()
    with Image.open(destination) as loaded:
        assert loaded.size == (4, 4)
