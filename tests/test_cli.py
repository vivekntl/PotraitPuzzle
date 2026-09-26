from pathlib import Path

from PIL import Image

from puzzle_portrait.cli import main

FIXTURE = Path(__file__).parent / "fixtures" / "sample.png"


def test_cli_prints_image_info(capsys) -> None:
    exit_code = main(["info", str(FIXTURE)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "width: 8" in output
    assert "height: 8" in output
    assert "mode: RGB" in output
    assert "aspect_ratio: 1.0" in output


def test_cli_missing_image_prints_error(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.png"

    exit_code = main(["info", str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Image not found" in captured.err


def test_cli_preview_saves_100x100_image(tmp_path: Path, capsys) -> None:
    exit_code = main(["preview", str(FIXTURE), "--output-dir", str(tmp_path)])

    output_path = tmp_path / "sample_preview.png"
    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(output_path) in captured.out
    assert output_path.is_file()

    with Image.open(output_path) as preview:
        assert preview.size == (100, 100)
