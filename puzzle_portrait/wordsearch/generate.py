"""Generate a word-search by placing a list of words on a letter grid."""

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from puzzle_portrait.wordsearch.directions import (
    DIRECTIONS,
    Direction,
    normalize_direction_weights,
)
from puzzle_portrait.wordsearch.fill import fill_empty_random, resolve_fill_percent
from puzzle_portrait.wordsearch.letter_grid import LetterGrid
from puzzle_portrait.wordsearch.placement import (
    Placement,
    _valid_placements,
    can_place,
    place_word,
)
from puzzle_portrait.wordsearch.score import (
    axis_counts,
    choose_scored_placement,
    occupied_cells,
    score_placement,
    uses_placement_scoring,
)
from puzzle_portrait.wordsearch.word_list import WordSpec, parse_word_line


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
    spread_words: bool = False,
    balance_directions: bool = False,
    direction_weights: Mapping[Direction, float] | None = None,
    fill_empty: bool | None = None,
    fill_percent: int | None = None,
    allow_phrases: bool = True,
    spread_rate: float = 1.0,
) -> WordSearch:
    """Place ``words`` on a new grid, overlapping only when letters agree.

    Uses ``seed`` to choose among valid positions and directions. When
    ``spread_words`` is true, the first words prefer the center and later
    words move outward. ``spread_rate`` controls how quickly that radius
    grows. ``balance_directions`` optionally discourages packing most words
    on the same axis. ``direction_weights`` scales each direction (missing
    keys default to 1). Words that cannot be placed are listed in
    ``failed_words`` instead of being dropped silently.

    With scoring off, the seeded choice is the original uniform pick. With
    scoring on, the same seed still produces the same puzzle.

    ``allow_phrases`` keeps unpinned entries that contain spaces as one
    placement. A line may end with ``{{row, col}, DIRECTION}`` to pin the
    first letter; pinned entries are placed before unpinned ones and skip
    random choice. ``fill_percent`` (0–100) is the share of leftover tiles
    filled with random letters. ``fill_empty`` is the older on/off form.
    """
    allowed = tuple(directions)
    if not allowed:
        raise ValueError("At least one direction is required")
    if spread_rate < 0:
        raise ValueError(f"Spread rate must be zero or positive, got {spread_rate}")
    percent = resolve_fill_percent(fill_percent, fill_empty)
    scoring_weights = None
    if direction_weights:
        for weight in direction_weights.values():
            if weight < 0:
                raise ValueError(f"Direction weight must be >= 0, got {weight}")
        allowed = tuple(
            direction
            for direction in allowed
            if direction_weights.get(direction, 1.0) > 0
        )
        if not allowed:
            raise ValueError("At least one direction is required")
        scoring_weights = normalize_direction_weights(direction_weights, allowed)

    grid = LetterGrid(width, height)
    rng = random.Random(seed)
    placements: list[Placement] = []
    failed_words: list[str] = []
    scoring = uses_placement_scoring(
        spread_words=spread_words,
        balance_directions=balance_directions,
        direction_weights=direction_weights,
    )

    specs: list[WordSpec] = []
    for raw in words:
        try:
            specs.append(parse_word_line(raw))
        except ValueError:
            failed_words.append(str(raw).strip() or str(raw))

    for spec in specs:
        if spec.row is None or spec.column is None or spec.direction is None:
            continue
        if not can_place(grid, spec.word, spec.row, spec.column, spec.direction):
            failed_words.append(spec.source)
            continue
        place_word(grid, spec.word, spec.row, spec.column, spec.direction)
        placements.append(
            Placement(
                word=spec.word,
                row=spec.row,
                column=spec.column,
                direction=spec.direction,
            )
        )

    for spec in specs:
        if spec.is_pinned():
            continue
        word = spec.word
        if not allow_phrases and _contains_whitespace(word):
            failed_words.append(spec.source)
            continue
        candidates = _valid_placements(grid, word, allowed)
        if not candidates:
            failed_words.append(spec.source)
            continue

        if scoring:
            used = occupied_cells(placements)
            counts = axis_counts(placements)
            scores = [
                score_placement(
                    candidate,
                    occupied=used,
                    axis_counts=counts,
                    spread_words=spread_words,
                    balance_directions=balance_directions,
                    direction_weights=scoring_weights,
                    spread_rate=spread_rate,
                    grid_width=width,
                    grid_height=height,
                    placed_count=len(placements),
                )
                for candidate in candidates
            ]
            chosen = choose_scored_placement(rng, candidates, scores)
        else:
            chosen = rng.choice(candidates)
        place_word(grid, chosen.word, chosen.row, chosen.column, chosen.direction)
        placements.append(chosen)

    fill_empty_random(grid, rng=rng, percent=percent)

    return WordSearch(
        grid=grid,
        placements=tuple(placements),
        failed_words=tuple(failed_words),
    )


def _contains_whitespace(word: str) -> bool:
    return any(character.isspace() for character in word)
