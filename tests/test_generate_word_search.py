import pytest

from puzzle_portrait.wordsearch import (
    DOWN,
    EMPTY,
    FORWARD_DIRECTIONS,
    LEFT,
    RIGHT,
    UP,
    direction_weights_from_axes,
    distance_from_center,
    generate_word_search,
    placement_middle_letter,
)


def _letters_along(puzzle, placement) -> str:
    return "".join(
        puzzle.grid[
            placement.row + offset * placement.direction.d_row,
            placement.column + offset * placement.direction.d_column,
        ]
        for offset, _ in enumerate(placement.word)
    )


def test_generate_places_all_words_and_returns_metadata() -> None:
    puzzle = generate_word_search(
        8,
        8,
        ["CAT", "DOG", "BIRD"],
        directions=(RIGHT, DOWN),
        seed=11,
    )

    assert puzzle.failed_words == ()
    assert {placement.word for placement in puzzle.placements} == {"CAT", "DOG", "BIRD"}
    assert puzzle.grid.dimensions == (8, 8)
    for placement in puzzle.placements:
        assert placement.direction in (RIGHT, DOWN)
        assert _letters_along(puzzle, placement) == placement.word


def test_generate_allows_overlap_when_letters_agree() -> None:
    puzzle = generate_word_search(
        5,
        1,
        ["CAT", "AT"],
        directions=(RIGHT,),
        seed=0,
    )

    assert puzzle.failed_words == ()
    assert len(puzzle.placements) == 2
    assert _letters_along(puzzle, puzzle.placements[0]) == "CAT"
    assert _letters_along(puzzle, puzzle.placements[1]) == "AT"


def test_generate_is_reproducible_with_the_same_seed() -> None:
    words = ["ONE", "TWO", "TEN"]
    first = generate_word_search(7, 7, words, seed=42)
    second = generate_word_search(7, 7, words, seed=42)

    assert first.placements == second.placements
    assert first.failed_words == second.failed_words
    for row in range(7):
        for column in range(7):
            assert first.grid[row, column] == second.grid[row, column]


def test_generate_reports_words_that_cannot_be_placed() -> None:
    puzzle = generate_word_search(
        3,
        3,
        ["HI", "TOOLONG", "OK"],
        directions=(RIGHT,),
        seed=3,
    )

    assert "TOOLONG" in puzzle.failed_words
    assert "HI" not in puzzle.failed_words
    assert "OK" not in puzzle.failed_words
    assert {placement.word for placement in puzzle.placements} == {"HI", "OK"}


def test_generate_respects_allowed_directions() -> None:
    puzzle = generate_word_search(
        6,
        6,
        ["HELLO"],
        directions=(DOWN,),
        seed=5,
    )

    assert puzzle.failed_words == ()
    assert puzzle.placements[0].direction == DOWN
    assert _letters_along(puzzle, puzzle.placements[0]) == "HELLO"


def test_spread_words_is_deterministic_with_a_seed() -> None:
    words = ["CAT", "DOG", "BIRD", "FISH"]
    first = generate_word_search(10, 10, words, seed=17, spread_words=True)
    second = generate_word_search(10, 10, words, seed=17, spread_words=True)

    assert first.placements == second.placements
    assert first.failed_words == second.failed_words
    for row in range(10):
        for column in range(10):
            assert first.grid[row, column] == second.grid[row, column]


def test_diagonal_weight_two_does_not_take_every_word() -> None:
    from collections import Counter

    from puzzle_portrait.wordsearch import axis_of

    words = ["ONE", "TWO", "SIX", "TEN", "RED", "BLUE", "FOX", "OWL", "SUN", "SKY"]
    weights = direction_weights_from_axes(horizontal=1, vertical=1, diagonal=2)
    shares = []
    for seed in range(8):
        puzzle = generate_word_search(
            16,
            16,
            words,
            directions=FORWARD_DIRECTIONS,
            seed=seed,
            spread_words=False,
            direction_weights=weights,
            fill_empty=False,
        )
        counts = Counter(axis_of(placement.direction) for placement in puzzle.placements)
        shares.append(counts["diagonal"] / len(puzzle.placements))

    mean_diagonal = sum(shares) / len(shares)
    assert 0.3 < mean_diagonal < 0.75


def test_direction_weights_can_forbid_an_axis() -> None:
    weights = direction_weights_from_axes(horizontal=0, vertical=1, diagonal=0)
    puzzle = generate_word_search(
        8,
        8,
        ["HELLO", "WORLD", "CAT"],
        seed=4,
        direction_weights=weights,
    )

    assert puzzle.failed_words == ()
    assert {placement.direction for placement in puzzle.placements} <= {DOWN, UP}


def test_balance_directions_reduces_one_axis_dominating() -> None:
    from collections import Counter

    from puzzle_portrait.wordsearch import axis_of

    words = ["ONE", "TWO", "SIX", "TEN", "RED", "BLUE", "FOX", "OWL", "SUN", "SKY"]

    def max_axis_share(*, balance: bool) -> float:
        shares = []
        for seed in range(6):
            puzzle = generate_word_search(
                14,
                14,
                words,
                seed=seed,
                spread_words=False,
                balance_directions=balance,
            )
            counts = Counter(axis_of(placement.direction) for placement in puzzle.placements)
            shares.append(max(counts.values()) / len(puzzle.placements))
        return sum(shares) / len(shares)

    assert max_axis_share(balance=True) < max_axis_share(balance=False)


def test_generate_places_a_phrase_as_one_entry() -> None:
    puzzle = generate_word_search(
        12,
        1,
        ["SOMEONE COOL"],
        directions=(RIGHT,),
        seed=0,
        fill_empty=False,
        allow_phrases=True,
    )

    assert puzzle.failed_words == ()
    assert puzzle.placements[0].word == "SOMEONE COOL"
    assert _letters_along(puzzle, puzzle.placements[0]) == "SOMEONE COOL"
    assert "".join(puzzle.grid[0, column] for column in range(12)) == "SOMEONE COOL"


def test_generate_rejects_phrases_when_disallowed() -> None:
    puzzle = generate_word_search(
        12,
        1,
        ["SOMEONE COOL", "HI"],
        directions=(RIGHT,),
        seed=0,
        fill_empty=False,
        allow_phrases=False,
    )

    assert puzzle.failed_words == ("SOMEONE COOL",)
    assert {placement.word for placement in puzzle.placements} == {"HI"}


def test_generate_can_skip_filler_letters() -> None:
    puzzle = generate_word_search(
        5,
        1,
        ["HI"],
        directions=(RIGHT,),
        seed=0,
        fill_empty=False,
    )

    letters = [puzzle.grid[0, column] for column in range(5)]
    assert letters.count("H") == 1
    assert letters.count("I") == 1
    assert letters.count(EMPTY) == 3


def test_generate_without_backwards_uses_only_forward_directions() -> None:
    puzzle = generate_word_search(
        8,
        8,
        ["CAT", "DOG", "BIRD"],
        directions=FORWARD_DIRECTIONS,
        seed=3,
        fill_empty=False,
    )

    assert puzzle.failed_words == ()
    assert {placement.direction for placement in puzzle.placements} <= set(
        FORWARD_DIRECTIONS
    )
    assert LEFT not in {placement.direction for placement in puzzle.placements}


def test_spread_words_starts_near_the_center() -> None:
    words = ["CAT", "DOG", "BIRD", "FISH"]
    centered = [
        distance_from_center(
            generate_word_search(
                12,
                12,
                words,
                seed=seed,
                spread_words=True,
                spread_rate=1.0,
                fill_empty=False,
            ).placements[0],
            12,
            12,
        )
        for seed in range(8)
    ]
    random_first = [
        distance_from_center(
            generate_word_search(
                12,
                12,
                words,
                seed=seed,
                spread_words=False,
                fill_empty=False,
            ).placements[0],
            12,
            12,
        )
        for seed in range(8)
    ]

    assert sum(centered) / len(centered) < sum(random_first) / len(random_first)
    assert sum(centered) / len(centered) < 3.0


def test_first_word_puts_middle_letter_on_the_center_tile() -> None:
    middles = []
    starts = []
    for seed in range(8):
        puzzle = generate_word_search(
            15,
            15,
            ["HELLO", "WORLD", "CAT"],
            seed=seed,
            spread_words=True,
            spread_rate=1.0,
            fill_empty=False,
        )
        first = puzzle.placements[0]
        assert first.word == "HELLO"
        middles.append(placement_middle_letter(first))
        starts.append((first.row, first.column))

    assert all(abs(row - 7) <= 1 and abs(column - 7) <= 1 for row, column in middles)
    assert (7, 7) not in starts


def test_higher_spread_rate_pushes_later_words_outward() -> None:
    words = ["ONE", "TWO", "SIX", "TEN", "RED", "BLUE", "FOX", "OWL"]

    def mean_later_distance(rate: float) -> float:
        distances = []
        for seed in range(6):
            puzzle = generate_word_search(
                14,
                14,
                words,
                seed=seed,
                spread_words=True,
                spread_rate=rate,
                fill_empty=False,
            )
            later = puzzle.placements[-3:]
            distances.extend(
                distance_from_center(placement, 14, 14) for placement in later
            )
        return sum(distances) / len(distances)

    assert mean_later_distance(2.5) > mean_later_distance(0.3)


def test_generate_rejects_negative_spread_rate() -> None:
    with pytest.raises(ValueError, match="Spread rate"):
        generate_word_search(5, 5, ["HI"], spread_words=True, spread_rate=-1)


def test_generate_rejects_negative_direction_weights() -> None:
    with pytest.raises(ValueError, match="weight"):
        generate_word_search(
            5,
            5,
            ["HI"],
            direction_weights={RIGHT: -1},
        )
