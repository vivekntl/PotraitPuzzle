import pytest

from puzzle_portrait.grid import Cell, Grid, RGB


def test_create_grid_has_requested_dimensions() -> None:
    grid = Grid(4, 3)

    assert grid.width == 4
    assert grid.height == 3
    assert grid.dimensions == (4, 3)


def test_create_grid_fills_cells_with_position_and_color() -> None:
    fill = RGB(10, 20, 30)
    grid = Grid(2, 3, color=fill)

    for row in range(3):
        for column in range(2):
            cell = grid[row, column]
            assert isinstance(cell, Cell)
            assert cell.row == row
            assert cell.column == column
            assert cell.color == fill
            assert cell.character is None


def test_index_returns_cell_at_row_and_column() -> None:
    grid = Grid(3, 2, color=RGB(1, 2, 3))

    cell = grid[1, 2]

    assert cell.row == 1
    assert cell.column == 2
    assert cell.color == RGB(1, 2, 3)


def test_index_assignment_updates_color_and_keeps_position() -> None:
    grid = Grid(3, 2)
    grid[1, 2] = RGB(255, 128, 0)

    cell = grid[1, 2]
    assert cell.color == RGB(255, 128, 0)
    assert cell.row == 1
    assert cell.column == 2
    assert grid[0, 0].color == RGB(0, 0, 0)


def test_index_out_of_bounds_raises() -> None:
    grid = Grid(2, 2)

    with pytest.raises(IndexError, match="outside"):
        grid[2, 0]
    with pytest.raises(IndexError, match="outside"):
        grid[0, 2]
    with pytest.raises(IndexError, match="outside"):
        grid[-1, 0]


def test_create_grid_rejects_non_positive_size() -> None:
    with pytest.raises(ValueError, match="1x1"):
        Grid(0, 3)
    with pytest.raises(ValueError, match="1x1"):
        Grid(2, 0)


def test_rgb_rejects_out_of_range_channel() -> None:
    with pytest.raises(ValueError, match="red"):
        RGB(256, 0, 0)


def test_cell_can_hold_optional_character() -> None:
    cell = Cell(row=1, column=2, color=RGB(1, 2, 3), character="A")

    assert cell.color == RGB(1, 2, 3)
    assert cell.character == "A"


def test_set_character_keeps_color() -> None:
    grid = Grid(2, 2, color=RGB(9, 8, 7))

    grid.set_character(0, 1, "Z")

    cell = grid[0, 1]
    assert cell.character == "Z"
    assert cell.color == RGB(9, 8, 7)
    assert grid[0, 0].character is None


def test_setting_color_preserves_character() -> None:
    grid = Grid(2, 1, color=RGB(1, 1, 1))
    grid.set_character(0, 0, "Q")

    grid[0, 0] = RGB(4, 5, 6)

    assert grid[0, 0].color == RGB(4, 5, 6)
    assert grid[0, 0].character == "Q"


def test_cell_rejects_multi_character_value() -> None:
    with pytest.raises(ValueError, match="single character"):
        Cell(row=0, column=0, color=RGB(0, 0, 0), character="AB")
