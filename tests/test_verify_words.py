from puzzle_portrait.wordsearch import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    LetterGrid,
    place_word,
    verify_words,
)


def test_verify_finds_overlapping_words() -> None:
    grid = LetterGrid(5, 1)
    place_word(grid, "CAT", 0, 0, RIGHT)

    report = verify_words(grid, ["CAT", "AT"], directions=(RIGHT,))

    assert report.all_found
    cat, at = report.results
    assert cat.found
    assert cat.locations[0].row == 0
    assert cat.locations[0].column == 0
    assert cat.locations[0].direction == RIGHT
    assert at.found
    assert at.locations[0].row == 0
    assert at.locations[0].column == 1
    assert at.locations[0].direction == RIGHT


def test_verify_finds_reversed_words() -> None:
    grid = LetterGrid(5, 3)
    place_word(grid, "CAT", 1, 0, RIGHT)
    place_word(grid, "DOG", 0, 3, DOWN)

    report = verify_words(grid, ["TAC", "GOD"], directions=(LEFT, UP))

    assert report.all_found
    tac, god = report.results
    assert (tac.locations[0].row, tac.locations[0].column, tac.locations[0].direction) == (
        1,
        2,
        LEFT,
    )
    assert (god.locations[0].row, god.locations[0].column, god.locations[0].direction) == (
        2,
        3,
        UP,
    )


def test_verify_reports_missing_words() -> None:
    grid = LetterGrid(4, 2)
    place_word(grid, "HI", 0, 0, RIGHT)

    report = verify_words(grid, ["HI", "BYE"], directions=(RIGHT, LEFT))

    assert not report.all_found
    assert report.results[0].found
    assert report.results[0].word == "HI"
    assert not report.results[1].found
    assert report.results[1].word == "BYE"
    assert report.results[1].locations == ()


def test_verify_respects_allowed_directions() -> None:
    grid = LetterGrid(4, 1)
    place_word(grid, "CAT", 0, 0, RIGHT)

    only_down = verify_words(grid, ["CAT"], directions=(DOWN,))
    only_left = verify_words(grid, ["CAT"], directions=(LEFT,))
    both = verify_words(grid, ["CAT", "TAC"], directions=(RIGHT, LEFT))

    assert not only_down.all_found
    assert not only_left.results[0].found
    assert both.results[0].found
    assert both.results[1].found
    assert both.results[1].locations[0].direction == LEFT
