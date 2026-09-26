"""Generate a word-search by placing a list of words on a letter grid."""

import random
from collections.abc import Sequence
from dataclasses import dataclass

from puzzle_portrait.wordsearch.directions import DIRECTIONS, Direction
from puzzle_portrait.wordsearch.fill import fill_empty_random
from puzzle_portrait.wordsearch.letter_grid import LetterGrid
from puzzle_portrait.wordsearch.placement import Placement, _valid_placements, place_word


@dataclass(frozen=True, slots=True)
class WordSearch:
    """A generated letter grid with placement metadata."""

    grid: LetterGrid
    placements: tuple[Placement, ...]
    failed_words: tuple[str, ...]


def generate_word_search(
    width: int,
    height: int,
    words: Sequence[str],
    *,
    directions: Sequence[Direction] = DIRECTIONS,
    seed: int | None = None,
) -> WordSearch:
    """Place ``words`` on a new grid, overlapping only when letters agree.

    Uses ``seed`` to choose among valid positions and directions. Words that
    cannot be placed are listed in ``failed_words`` instead of being dropped
    silently.
    """
    allowed = tuple(directions)
    if not allowed:
        raise ValueError("At least one direction is required")

    grid = LetterGrid(width, height)
    rng = random.Random(seed)
    placements: list[Placement] = []
    failed_words: list[str] = []

    for word in words:
        candidates = _valid_placements(grid, word, allowed)
        if not candidates:
            failed_words.append(word)
            continue

        chosen = rng.choice(candidates)
        place_word(grid, chosen.word, chosen.row, chosen.column, chosen.direction)
        placements.append(chosen)

    fill_empty_random(grid, rng=rng)

    return WordSearch(
        grid=grid,
        placements=tuple(placements),
        failed_words=tuple(failed_words),
    )
