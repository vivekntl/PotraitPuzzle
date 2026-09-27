"""Score word placements for spatial spread and direction mix."""

from __future__ import annotations

import math
import random
from collections import Counter
from collections.abc import Mapping, Sequence

from puzzle_portrait.wordsearch.directions import Direction, axis_of
from puzzle_portrait.wordsearch.placement import Placement

_EQUAL_WEIGHT_EPS = 1e-12


def placement_cells(placement: Placement) -> list[tuple[int, int]]:
    """Return every grid cell occupied by ``placement``."""
    return [
        (
            placement.row + offset * placement.direction.d_row,
            placement.column + offset * placement.direction.d_column,
        )
        for offset in range(len(placement.word))
    ]


def placement_centroid(placement: Placement) -> tuple[float, float]:
    """Return the average row and column of ``placement``."""
    cells = placement_cells(placement)
    rows = sum(row for row, _ in cells)
    columns = sum(column for _, column in cells)
    count = len(cells)
    return rows / count, columns / count


def placement_middle_letter(placement: Placement) -> tuple[int, int]:
    """Return the cell that holds the middle letter of ``placement``.

    For ``CAT`` that is A; for ``HELLO`` that is L. Even-length words use the
    letter just before the midpoint (``HI`` → H, ``BIRD`` → I).
    """
    offset = (len(placement.word) - 1) // 2
    return (
        placement.row + offset * placement.direction.d_row,
        placement.column + offset * placement.direction.d_column,
    )


def spatial_score(
    placement: Placement,
    occupied: Sequence[tuple[int, int]],
) -> float:
    """Higher when ``placement`` sits farther from already used word cells."""
    if not occupied:
        return 1.0
    return min(
        math.hypot(row - used_row, column - used_column)
        for row, column in placement_cells(placement)
        for used_row, used_column in occupied
    )


def grid_center(width: int, height: int) -> tuple[float, float]:
    """Return the row/column center of a ``width`` by ``height`` grid."""
    return (height - 1) / 2.0, (width - 1) / 2.0


def distance_from_center(placement: Placement, width: int, height: int) -> float:
    """Return how far the middle letter is from the grid's center tile."""
    row, column = placement_middle_letter(placement)
    center_row, center_column = grid_center(width, height)
    return math.hypot(row - center_row, column - center_column)


def target_spread_radius(
    *,
    placed_count: int,
    spread_rate: float,
    width: int,
    height: int,
) -> float:
    """Preferred distance from center after ``placed_count`` words."""
    if spread_rate < 0:
        raise ValueError(f"Spread rate must be zero or positive, got {spread_rate}")
    farthest = math.hypot((height - 1) / 2.0, (width - 1) / 2.0)
    if farthest <= 0:
        return 0.0
    return min(farthest, placed_count * farthest * 0.18 * spread_rate)


def center_out_score(
    placement: Placement,
    *,
    width: int,
    height: int,
    placed_count: int,
    spread_rate: float,
) -> float:
    """Higher when ``placement`` sits near the current outward ring."""
    target = target_spread_radius(
        placed_count=placed_count,
        spread_rate=spread_rate,
        width=width,
        height=height,
    )
    error = abs(distance_from_center(placement, width, height) - target)
    # Tight enough that a start-at-center word (middle letter offset) loses
    # to one whose middle letter sits on the center tile.
    sigma = 0.45
    return math.exp(-0.5 * (error / sigma) ** 2)


def direction_balance_score(
    direction: Direction,
    axis_counts: Mapping[str, int],
) -> float:
    """Higher when ``direction``'s axis lags the most-used axis."""
    count = axis_counts.get(axis_of(direction), 0)
    leader = max(axis_counts.values(), default=0)
    return ((1.0 + leader) / (1.0 + count)) ** 2


def score_placement(
    placement: Placement,
    *,
    occupied: Sequence[tuple[int, int]],
    axis_counts: Mapping[str, int],
    spread_words: bool,
    balance_directions: bool,
    direction_weights: Mapping[Direction, float] | None,
    spread_rate: float = 1.0,
    grid_width: int = 1,
    grid_height: int = 1,
    placed_count: int = 0,
) -> float:
    """Combine center-out spread, direction balance, and configured weights."""
    del occupied
    score = 1.0
    if spread_words:
        score *= center_out_score(
            placement,
            width=grid_width,
            height=grid_height,
            placed_count=placed_count,
            spread_rate=spread_rate,
        )
    if balance_directions:
        score *= direction_balance_score(placement.direction, axis_counts)
    if direction_weights:
        weight = direction_weights.get(placement.direction, 1.0)
        if weight < 0:
            raise ValueError(f"Direction weight must be >= 0, got {weight}")
        score *= weight
    return score


def choose_scored_placement(
    rng: random.Random,
    candidates: Sequence[Placement],
    scores: Sequence[float],
) -> Placement:
    """Pick a candidate with probability rising with score. Seeded via ``rng``."""
    if not candidates:
        raise ValueError("No placement candidates")
    if len(candidates) != len(scores):
        raise ValueError("Each candidate needs a score")
    weights = [max(float(score), 0.0) + 1e-9 for score in scores]
    return rng.choices(list(candidates), weights=weights, k=1)[0]


def uses_placement_scoring(
    *,
    spread_words: bool,
    balance_directions: bool,
    direction_weights: Mapping[Direction, float] | None,
) -> bool:
    """Return whether selection should use scores instead of uniform choice."""
    if spread_words or balance_directions:
        return True
    if not direction_weights:
        return False
    return any(abs(weight - 1.0) > _EQUAL_WEIGHT_EPS for weight in direction_weights.values())


def occupied_cells(placements: Sequence[Placement]) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    for placement in placements:
        cells.extend(placement_cells(placement))
    return cells


def axis_counts(placements: Sequence[Placement]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for placement in placements:
        counts[axis_of(placement.direction)] += 1
    return counts
