"""Check whether a word can be written onto a letter grid."""

import random
from dataclasses import dataclass

from puzzle_portrait.wordsearch.directions import DIRECTIONS, Direction
from puzzle_portrait.wordsearch.letter_grid import EMPTY, LetterGrid


@dataclass(frozen=True, slots=True)
class Placement:
    """Where a word was written on the grid."""

    word: str
    row: int
    column: int
    direction: Direction


def can_place(
    grid: LetterGrid,
    word: str,
    row: int,
    column: int,
    direction: Direction,
) -> bool:
    """Return whether ``word`` fits at ``(row, column)`` in ``direction``.

    A placement is valid when every destination cell is inside the grid and is
    either empty or already holds the same letter. The grid is not modified.
    """
    if not word:
        return False

    for offset, letter in enumerate(word):
        dest_row = row + offset * direction.d_row
        dest_column = column + offset * direction.d_column
        if not grid.in_bounds(dest_row, dest_column):
            return False
        existing = grid[dest_row, dest_column]
        if existing != EMPTY and existing != letter:
            return False

    return True


def place_word(
    grid: LetterGrid,
    word: str,
    row: int,
    column: int,
    direction: Direction,
) -> None:
    """Write ``word`` onto ``grid`` if the placement is valid.

    Invalid placements raise ``ValueError`` and leave the grid unchanged.
    """
    if not can_place(grid, word, row, column, direction):
        raise ValueError(
            f"Cannot place {word!r} at ({row}, {column}) in direction "
            f"({direction.d_row}, {direction.d_column})"
        )

    for offset, letter in enumerate(word):
        dest_row = row + offset * direction.d_row
        dest_column = column + offset * direction.d_column
        grid[dest_row, dest_column] = letter


def _valid_placements(
    grid: LetterGrid,
    word: str,
    directions: tuple[Direction, ...] = DIRECTIONS,
) -> list[Placement]:
    return [
        Placement(word=word, row=row, column=column, direction=direction)
        for row in range(grid.height)
        for column in range(grid.width)
        for direction in directions
        if can_place(grid, word, row, column, direction)
    ]


def place_word_randomly(
    grid: LetterGrid,
    word: str,
    *,
    seed: int | None = None,
    rng: random.Random | None = None,
    directions: tuple[Direction, ...] = DIRECTIONS,
) -> Placement:
    """Place ``word`` at one randomly chosen valid position and direction.

    ``seed`` or ``rng`` makes the choice reproducible. Raises ``ValueError`` if
    no valid placement exists; the grid is left unchanged in that case.
    """
    candidates = _valid_placements(grid, word, directions)
    if not candidates:
        raise ValueError(f"No valid placement for {word!r}")

    chooser = rng if rng is not None else random.Random(seed)
    chosen = chooser.choice(candidates)
    place_word(grid, chosen.word, chosen.row, chosen.column, chosen.direction)
    return chosen


