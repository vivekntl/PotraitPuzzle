"""Fill unused word-search cells with deterministic random letters."""

import random
import string

from puzzle_portrait.wordsearch.letter_grid import LetterGrid

ALPHABET = string.ascii_uppercase


def resolve_fill_percent(
    fill_percent: int | None = None,
    fill_empty: bool | None = None,
) -> int:
    """Return 0–100. ``fill_percent`` wins; otherwise ``fill_empty`` maps True→100, False→0."""
    if fill_percent is not None:
        if fill_percent < 0 or fill_percent > 100:
            raise ValueError(f"Fill percent must be 0-100, got {fill_percent}")
        return fill_percent
    return 100 if fill_empty is not False else 0


def fill_count(empty_count: int, percent: int) -> int:
    """How many of ``empty_count`` cells to fill for ``percent`` (round half up)."""
    if empty_count <= 0 or percent <= 0:
        return 0
    if percent >= 100:
        return empty_count
    return min(empty_count, (empty_count * percent + 50) // 100)


def fill_empty_random(
    grid: LetterGrid,
    *,
    seed: int | None = None,
    rng: random.Random | None = None,
    percent: int = 100,
) -> None:
    """Fill ``percent`` of empty cells with random uppercase letters.

    ``seed`` or ``rng`` makes the fill reproducible. 100% fills every empty
    cell in row-major order so existing puzzles stay the same.
    """
    percent = resolve_fill_percent(fill_percent=percent)
    if percent <= 0:
        return

    chooser = rng if rng is not None else random.Random(seed)
    if percent >= 100:
        for row in range(grid.height):
            for column in range(grid.width):
                if grid.is_empty(row, column):
                    grid[row, column] = chooser.choice(ALPHABET)
        return

    empty = [
        (row, column)
        for row in range(grid.height)
        for column in range(grid.width)
        if grid.is_empty(row, column)
    ]
    chooser.shuffle(empty)
    for row, column in empty[: fill_count(len(empty), percent)]:
        grid[row, column] = chooser.choice(ALPHABET)
