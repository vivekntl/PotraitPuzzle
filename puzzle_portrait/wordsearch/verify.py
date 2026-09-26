"""Search a letter grid for requested words."""

from collections.abc import Sequence
from dataclasses import dataclass

from puzzle_portrait.wordsearch.directions import DIRECTIONS, Direction
from puzzle_portrait.wordsearch.letter_grid import LetterGrid
from puzzle_portrait.wordsearch.placement import Placement


@dataclass(frozen=True, slots=True)
class WordResult:
    """Whether a target word was found, and every matching location."""

    word: str
    found: bool
    locations: tuple[Placement, ...]


@dataclass(frozen=True, slots=True)
class VerificationReport:
    """Verification results for each requested word, in request order."""

    results: tuple[WordResult, ...]

    @property
    def all_found(self) -> bool:
        return all(result.found for result in self.results)


def _matches_at(
    grid: LetterGrid,
    word: str,
    row: int,
    column: int,
    direction: Direction,
) -> bool:
    if not word:
        return False

    for offset, letter in enumerate(word):
        dest_row = row + offset * direction.d_row
        dest_column = column + offset * direction.d_column
        if not grid.in_bounds(dest_row, dest_column):
            return False
        if grid[dest_row, dest_column] != letter:
            return False

    return True


def find_word(
    grid: LetterGrid,
    word: str,
    directions: Sequence[Direction] = DIRECTIONS,
) -> tuple[Placement, ...]:
    """Return every in-bounds match of ``word`` in ``directions``."""
    return tuple(
        Placement(word=word, row=row, column=column, direction=direction)
        for row in range(grid.height)
        for column in range(grid.width)
        for direction in directions
        if _matches_at(grid, word, row, column, direction)
    )


def verify_words(
    grid: LetterGrid,
    words: Sequence[str],
    *,
    directions: Sequence[Direction] = DIRECTIONS,
) -> VerificationReport:
    """Search ``grid`` for each word in every allowed direction."""
    allowed = tuple(directions)
    results = []
    for word in words:
        locations = find_word(grid, word, allowed)
        results.append(
            WordResult(word=word, found=bool(locations), locations=locations)
        )
    return VerificationReport(results=tuple(results))
