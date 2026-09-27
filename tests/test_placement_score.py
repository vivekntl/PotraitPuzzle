import random

from puzzle_portrait.wordsearch.score import direction_balance_score

from puzzle_portrait.wordsearch import (
    DOWN,
    Placement,
    RIGHT,
    center_out_score,
    choose_scored_placement,
    distance_from_center,
    placement_cells,
    placement_centroid,
    placement_middle_letter,
    score_placement,
    spatial_score,
    target_spread_radius,
)


def test_placement_cells_follow_the_direction() -> None:
    placement = Placement("CAT", 1, 2, RIGHT)

    assert placement_cells(placement) == [(1, 2), (1, 3), (1, 4)]
    assert placement_centroid(placement) == (1.0, 3.0)
    assert placement_middle_letter(placement) == (1, 3)


def test_spatial_score_is_higher_when_farther_from_used_cells() -> None:
    near = Placement("HI", 0, 1, RIGHT)
    far = Placement("HI", 6, 6, DOWN)

    assert spatial_score(far, [(0, 0)]) > spatial_score(near, [(0, 0)])


def test_score_placement_applies_direction_weight() -> None:
    placement = Placement("HI", 0, 0, RIGHT)

    boosted = score_placement(
        placement,
        occupied=(),
        axis_counts={},
        spread_words=False,
        balance_directions=False,
        direction_weights={RIGHT: 4},
    )
    normal = score_placement(
        placement,
        occupied=(),
        axis_counts={},
        spread_words=False,
        balance_directions=False,
        direction_weights=None,
    )

    assert boosted == 4
    assert normal == 1


def test_center_out_score_prefers_the_current_ring() -> None:
    center = Placement("HI", 7, 7, RIGHT)
    edge = Placement("HI", 0, 0, RIGHT)

    assert center_out_score(
        center, width=16, height=16, placed_count=0, spread_rate=1
    ) > center_out_score(edge, width=16, height=16, placed_count=0, spread_rate=1)
    assert center_out_score(
        edge, width=16, height=16, placed_count=8, spread_rate=2
    ) > center_out_score(center, width=16, height=16, placed_count=8, spread_rate=2)
    assert center_out_score(
        center, width=16, height=16, placed_count=0, spread_rate=1
    ) > 20 * center_out_score(edge, width=16, height=16, placed_count=0, spread_rate=1)


def test_center_out_prefers_middle_letter_on_the_center_tile() -> None:
    # 15x15 has a single center tile at (7, 7). HELLO's middle letter is L.
    middle_on_center = Placement("HELLO", 7, 5, RIGHT)
    first_on_center = Placement("HELLO", 7, 7, RIGHT)

    assert placement_middle_letter(middle_on_center) == (7, 7)
    assert placement_middle_letter(first_on_center) == (7, 9)
    assert center_out_score(
        middle_on_center, width=15, height=15, placed_count=0, spread_rate=1
    ) > 20 * center_out_score(
        first_on_center, width=15, height=15, placed_count=0, spread_rate=1
    )


def test_target_radius_grows_with_rate_and_word_count() -> None:
    slow = target_spread_radius(placed_count=3, spread_rate=0.5, width=20, height=20)
    fast = target_spread_radius(placed_count=3, spread_rate=2.0, width=20, height=20)
    later = target_spread_radius(placed_count=8, spread_rate=0.5, width=20, height=20)

    assert fast > slow
    assert later > slow
    assert target_spread_radius(placed_count=0, spread_rate=3, width=20, height=20) == 0
    assert distance_from_center(Placement("A", 0, 0, RIGHT), 9, 9) > 0


def test_direction_balance_prefers_a_lagging_axis() -> None:
    used = {"horizontal": 4, "vertical": 0, "diagonal": 1}

    assert direction_balance_score(DOWN, used) > direction_balance_score(RIGHT, used)


def test_choose_scored_placement_keeps_lower_scores_in_play() -> None:
    from collections import Counter

    candidates = [
        Placement("HI", 0, 0, RIGHT),
        Placement("HI", 1, 0, DOWN),
    ]
    scores = [1.0, 2.0]
    counts: Counter = Counter()
    for seed in range(200):
        chosen = choose_scored_placement(random.Random(seed), candidates, scores)
        counts[chosen.direction] += 1

    assert counts[RIGHT] > 30
    assert counts[DOWN] > counts[RIGHT]


def test_choose_scored_placement_is_deterministic() -> None:
    candidates = [
        Placement("HI", 0, 0, RIGHT),
        Placement("HI", 1, 0, DOWN),
    ]
    scores = [1.0, 3.0]

    first = choose_scored_placement(random.Random(9), candidates, scores)
    second = choose_scored_placement(random.Random(9), candidates, scores)

    assert first == second
