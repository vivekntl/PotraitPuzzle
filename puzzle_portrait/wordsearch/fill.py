"""Fill unused word-search cells with deterministic random letters."""

import random
import string

from puzzle_portrait.wordsearch.letter_grid import LetterGrid

ALPHABET = string.ascii_uppercase


def fill_empty_random(
    grid: LetterGrid,
    *,
    seed: int | None = None,
    rng: random.Random | None = None,
) -> None:
    """Replace every empty cell with a random uppercase letter.

    ``seed`` or ``rng`` makes the fill reproducible.
    """
    chooser = rng if rng is not None else random.Random(seed)
    for row in range(grid.height):
        for column in range(grid.width):
            if grid.is_empty(row, column):
                grid[row, column] = chooser.choice(ALPHABET)
