import json
from pathlib import Path

from PIL import Image

from puzzle_portrait.config import (
    CONFIG_FILENAME,
    MOSAIC_FILENAME,
    MOSAIC_LETTERS_FILENAME,
    MOSAIC_LETTERS_SVG_FILENAME,
    MOSAIC_SVG_FILENAME,
    WORDS_FILENAME,
)
from puzzle_portrait.project import (
    ProjectSettings,
    load_project,
    save_project,
    settings_from_dict,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample.png"


def _settings(**overrides) -> ProjectSettings:
    values = dict(
        image="input.png",
        words=("CAT", "DOG"),
        words_file=WORDS_FILENAME,
        seed=7,
        color_count=16,
        crop_x=1,
        crop_y=2,
        crop_width=6,
        crop_height=5,
        columns=10,
        rows=8,
        tile_size=12,
        font="Arial",
        font_file=None,
        font_size=14,
        grid_lines=True,
        mosaic=MOSAIC_FILENAME,
        mosaic_letters=MOSAIC_LETTERS_FILENAME,
        failed_words=(),
    )
    values.update(overrides)
    return ProjectSettings(**values)


def test_save_project_writes_config_words_input_and_outputs(tmp_path: Path) -> None:
    mosaic = Image.new("RGB", (4, 4), (10, 20, 30))
    letters = Image.new("RGB", (4, 4), (40, 50, 60))

    config_path = save_project(
        tmp_path,
        _settings(),
        source_image=FIXTURE,
        mosaic=mosaic,
        mosaic_letters=letters,
        mosaic_svg="<svg xmlns='http://www.w3.org/2000/svg'></svg>",
        mosaic_letters_svg="<svg xmlns='http://www.w3.org/2000/svg'><text>A</text></svg>",
        mosaic_letters_svgs={
            "regular": "<svg xmlns='http://www.w3.org/2000/svg'><text>R</text></svg>",
            "bold": "<svg xmlns='http://www.w3.org/2000/svg'><text>B</text></svg>",
        },
    )

    assert config_path == tmp_path / CONFIG_FILENAME
    assert (tmp_path / "input.png").is_file()
    assert (tmp_path / WORDS_FILENAME).read_text(encoding="utf-8") == "CAT\nDOG\n"
    assert (tmp_path / MOSAIC_FILENAME).is_file()
    assert (tmp_path / MOSAIC_LETTERS_FILENAME).is_file()
    assert (tmp_path / MOSAIC_SVG_FILENAME).is_file()
    assert (tmp_path / MOSAIC_LETTERS_SVG_FILENAME).is_file()
    assert (tmp_path / "mosaic_letters_regular.svg").is_file()
    assert (tmp_path / "mosaic_letters_bold.svg").is_file()
    assert "B" in (tmp_path / "mosaic_letters_bold.svg").read_text(encoding="utf-8")

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert payload["image"] == "input.png"
    assert payload["words"] == ["CAT", "DOG"]
    assert payload["seed"] == 7
    assert payload["crop"] == {"x": 1, "y": 2, "width": 6, "height": 5}
    assert payload["outputs"]["mosaic"] == MOSAIC_FILENAME
    assert payload["outputs"]["mosaic_svg"] == MOSAIC_SVG_FILENAME
    assert payload["outputs"]["mosaic_letters_svg"] == MOSAIC_LETTERS_SVG_FILENAME
    assert payload["outputs"]["mosaic_letters_svgs"]["bold"] == "mosaic_letters_bold.svg"
    assert payload["allow_phrases"] is True
    assert payload["fill_empty"] is True
    assert payload["allow_backwards"] is True


def test_load_project_restores_settings_from_folder(tmp_path: Path) -> None:
    save_project(
        tmp_path,
        _settings(seed=99, columns=12, rows=9),
        source_image=FIXTURE,
        mosaic=Image.new("RGB", (2, 2), (1, 2, 3)),
        mosaic_letters=Image.new("RGB", (2, 2), (4, 5, 6)),
    )

    settings, folder = load_project(tmp_path)

    assert folder == tmp_path
    assert settings.seed == 99
    assert settings.columns == 12
    assert settings.rows == 9
    assert settings.words == ("CAT", "DOG")
    assert (folder / settings.image).is_file()


def test_load_project_prefers_words_file(tmp_path: Path) -> None:
    save_project(
        tmp_path,
        _settings(words=("OLD",)),
        source_image=FIXTURE,
        mosaic=Image.new("RGB", (2, 2), (1, 2, 3)),
        mosaic_letters=Image.new("RGB", (2, 2), (4, 5, 6)),
    )
    (tmp_path / WORDS_FILENAME).write_text("NEW\nWORD\n", encoding="utf-8")

    settings, _folder = load_project(tmp_path / CONFIG_FILENAME)

    assert settings.words == ("NEW", "WORD")


def test_settings_from_dict_reads_nested_crop_and_outputs() -> None:
    settings = settings_from_dict(
        {
            "image": "input.jpg",
            "words": ["HI"],
            "seed": 3,
            "color_count": 8,
            "crop": {"x": 0, "y": 1, "width": 4, "height": 5},
            "columns": 6,
            "rows": 7,
            "tile_size": 8,
            "font": "Calibri",
            "font_size": 11,
            "outputs": {"mosaic": "a.png", "mosaic_letters": "b.png"},
        }
    )

    assert settings.crop_y == 1
    assert settings.mosaic == "a.png"
    assert settings.mosaic_letters == "b.png"
    assert settings.words == ("HI",)
    assert settings.spread_words is False
    assert settings.spread_rate == 1.0
    assert settings.balance_directions is False
    assert settings.allow_phrases is True
    assert settings.fill_empty is True
    assert settings.allow_backwards is True


def test_settings_from_dict_reads_placement_scoring() -> None:
    settings = settings_from_dict(
        {
            "image": "input.jpg",
            "words": ["HI"],
            "seed": 3,
            "color_count": 8,
            "crop": {"x": 0, "y": 1, "width": 4, "height": 5},
            "columns": 6,
            "rows": 7,
            "tile_size": 8,
            "font": "Calibri",
            "font_size": 11,
            "spread_words": True,
            "spread_rate": 2.5,
            "balance_directions": True,
            "allow_phrases": False,
            "fill_empty": False,
            "allow_backwards": False,
            "direction_weights": {
                "horizontal": 0.5,
                "vertical": 2,
                "diagonal": 1.5,
            },
        }
    )

    assert settings.spread_words is True
    assert settings.spread_rate == 2.5
    assert settings.balance_directions is True
    assert settings.allow_phrases is False
    assert settings.fill_empty is False
    assert settings.allow_backwards is False
    assert settings.horizontal_weight == 0.5
    assert settings.vertical_weight == 2
    assert settings.diagonal_weight == 1.5
