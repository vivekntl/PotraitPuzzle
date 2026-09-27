from pathlib import Path

from puzzle_portrait.grid import RGB
from puzzle_portrait.image import load_image
from puzzle_portrait.ui.preview_job import PreviewSettings, render_preview
from puzzle_portrait.wordsearch import FORWARD_DIRECTIONS

FIXTURE = Path(__file__).parent / "fixtures" / "sample.png"


def test_render_preview_builds_a_lettered_mosaic() -> None:
    settings = PreviewSettings(
        crop_x=0,
        crop_y=0,
        crop_width=8,
        crop_height=8,
        columns=6,
        rows=4,
        color_count=8,
        words=("HI",),
        seed=1,
        spread_words=False,
        spread_rate=1.0,
        balance_directions=False,
        direction_weights=None,
        directions=FORWARD_DIRECTIONS,
        fill_empty=False,
        allow_phrases=False,
        tile_size=10,
        font=None,
        font_size=12,
        font_weight="regular",
        text_color_mode="black",
        text_color=RGB(0, 0, 0),
    )

    image = render_preview(load_image(FIXTURE), settings)

    assert image.size == (60, 40)
