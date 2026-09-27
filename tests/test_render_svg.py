from puzzle_portrait.grid import ColorGrid, RGB
from puzzle_portrait.render import render_color_grid_svg


def _sample_grid() -> ColorGrid:
    grid = ColorGrid(2, 2)
    grid[0, 0] = RGB(255, 0, 0)
    grid[0, 1] = RGB(0, 255, 0)
    grid[1, 0] = RGB(0, 0, 255)
    grid[1, 1] = RGB(255, 255, 0)
    return grid


def test_svg_uses_viewbox_for_print_scaling() -> None:
    svg = render_color_grid_svg(_sample_grid(), cell_size=10, draw_letters=False)

    assert 'viewBox="0 0 20 20"' in svg
    assert "<rect" in svg
    assert "#ff0000" in svg
    assert "#00ff00" in svg


def test_svg_draws_centered_letters() -> None:
    grid = ColorGrid(1, 1, color=RGB(0, 0, 0))
    grid.set_character(0, 0, "A")

    svg = render_color_grid_svg(
        grid,
        cell_size=20,
        font_size=12,
        font_family="Arial",
        auto_text_color=False,
        text_color=RGB(255, 255, 255),
    )

    assert ">A</text>" in svg
    assert 'text-anchor="middle"' in svg
    assert "#ffffff" in svg
    assert "Arial" in svg


def test_svg_escapes_letter_markup() -> None:
    grid = ColorGrid(1, 1, color=RGB(255, 255, 255))
    grid.set_character(0, 0, "<")

    svg = render_color_grid_svg(grid, cell_size=8, draw_letters=True)

    assert "&lt;" in svg
    assert "><</text>" not in svg


def test_svg_optional_grid_lines() -> None:
    with_lines = render_color_grid_svg(
        _sample_grid(),
        cell_size=8,
        grid_lines=True,
        draw_letters=False,
    )
    without = render_color_grid_svg(
        _sample_grid(),
        cell_size=8,
        grid_lines=False,
        draw_letters=False,
    )

    assert "<line" in with_lines
    assert "<line" not in without
