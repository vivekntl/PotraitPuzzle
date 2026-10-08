import pytest

from puzzle_portrait.wordsearch import (
    DOWN,
    DOWN_RIGHT,
    RIGHT,
    UP_RIGHT,
    parse_word_line,
)


def test_parse_plain_word() -> None:
    spec = parse_word_line("Hello")

    assert spec.word == "Hello"
    assert spec.is_pinned() is False
    assert spec.source == "Hello"


def test_parse_phrase_without_pin() -> None:
    spec = parse_word_line("My Name")

    assert spec.word == "My Name"
    assert spec.direction is None


def test_parse_pinned_horizontal() -> None:
    spec = parse_word_line("World {{2,4}, HOR}")

    assert spec.word == "World"
    assert spec.row == 2
    assert spec.column == 4
    assert spec.direction == RIGHT
    assert spec.is_pinned() is True


def test_parse_pinned_directions() -> None:
    assert parse_word_line("A {{0,0}, VER}").direction == DOWN
    assert parse_word_line("A {{0,0}, DIAG_LB_RU}").direction == UP_RIGHT
    assert parse_word_line("A {{0,0}, DIAG_LU_RB}").direction == DOWN_RIGHT


def test_parse_pinned_phrase_and_case_insensitive_direction() -> None:
    spec = parse_word_line("Is ABCD {{8,6}, diag_lb_ru}")

    assert spec.word == "Is ABCD"
    assert spec.row == 8
    assert spec.column == 6
    assert spec.direction == UP_RIGHT


def test_parse_rejects_unknown_direction() -> None:
    with pytest.raises(ValueError, match="Unknown direction"):
        parse_word_line("HI {{0,0}, LEFT}")


def test_parse_rejects_malformed_constraint() -> None:
    with pytest.raises(ValueError, match="Invalid placement constraint"):
        parse_word_line("HI {{0,0}}")
