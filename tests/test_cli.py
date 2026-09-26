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
    quantized_path = tmp_path / "sample_preview_16colors.png"
    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(output_path) in captured.out
    assert str(quantized_path) in captured.out
    assert output_path.is_file()
    assert quantized_path.is_file()

    with Image.open(output_path) as preview:
        assert preview.size == (100, 100)
    with Image.open(quantized_path) as quantized:
        assert quantized.size == (100, 100)


def test_cli_preview_respects_color_count(tmp_path: Path, capsys) -> None:
    exit_code = main(
        ["preview", str(FIXTURE), "--output-dir", str(tmp_path), "--colors", "8"]
    )

    quantized_path = tmp_path / "sample_preview_8colors.png"
    assert exit_code == 0
    assert quantized_path.is_file()
    assert "sample_preview_8colors.png" in capsys.readouterr().out


def test_cli_render_saves_mosaic_png(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "render",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--cell-size",
            "3",
            "--grid-lines",
        ]
    )

    mosaic_path = tmp_path / "sample_mosaic.png"
    assert exit_code == 0
    assert mosaic_path.is_file()
    assert str(mosaic_path) in capsys.readouterr().out

    with Image.open(mosaic_path) as mosaic:
        assert mosaic.size == (300, 300)
