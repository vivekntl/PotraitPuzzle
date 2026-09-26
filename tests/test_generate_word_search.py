from puzzle_portrait.wordsearch import (
    DOWN,
    RIGHT,
    generate_word_search,
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
