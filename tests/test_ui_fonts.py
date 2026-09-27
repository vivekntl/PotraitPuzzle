import sys

import pytest

from puzzle_portrait.render import available_font_weights, resolve_font_path
from puzzle_portrait.ui.fonts import font_file_for_family, list_system_fonts


def test_list_system_fonts_returns_named_files() -> None:
    fonts = list_system_fonts()

    assert fonts
    names = [family for family, path in fonts]
    assert names == sorted(names, key=str.casefold)
    assert all(path.is_file() for _, path in fonts)


def test_list_system_fonts_can_drop_style_variants() -> None:
    all_names = {family for family, _ in list_system_fonts()}
    regular = {family for family, _ in list_system_fonts(regular_only=True)}

    assert regular
    assert regular <= all_names
    assert all(not name.casefold().endswith(" bold") for name in regular)


@pytest.mark.skipif(sys.platform != "win32", reason="Arial is a Windows system font")
def test_font_file_for_family_resolves_arial() -> None:
    path = font_file_for_family("Arial")

    assert path is not None
    assert path.is_file()
    assert path.suffix.lower() in {".ttf", ".otf", ".ttc"}


@pytest.mark.skipif(sys.platform != "win32", reason="Arial Bold is a Windows system font")
def test_resolve_font_path_finds_arial_bold() -> None:
    regular = font_file_for_family("Arial")
    assert regular is not None

    bold = resolve_font_path(regular, "bold")

    assert bold.is_file()
    assert bold != regular


@pytest.mark.skipif(sys.platform != "win32", reason="Arial Bold is a Windows system font")
def test_available_font_weights_includes_arial_bold() -> None:
    regular = font_file_for_family("Arial")
    assert regular is not None

    weights = available_font_weights(regular)

    assert "regular" in weights
    assert "bold" in weights
