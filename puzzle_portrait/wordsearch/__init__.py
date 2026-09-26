"""Word placement and word-search puzzle generation."""

from puzzle_portrait.wordsearch.directions import (
    DIRECTIONS,
    DOWN,
    DOWN_LEFT,
    DOWN_RIGHT,
    LEFT,
    RIGHT,
    UP,
    UP_LEFT,
    UP_RIGHT,
    Direction,
)
from puzzle_portrait.wordsearch.fill import fill_empty_random
from puzzle_portrait.wordsearch.generate import WordSearch, generate_word_search
from puzzle_portrait.wordsearch.letter_grid import EMPTY, LetterGrid
from puzzle_portrait.wordsearch.placement import (
    Placement,
    can_place,
    place_word,
    place_word_randomly,
)
from puzzle_portrait.wordsearch.verify import (
    VerificationReport,
    WordResult,
    find_word,
    verify_words,
)

__all__ = [
    "DIRECTIONS",
    "DOWN",
    "DOWN_LEFT",
    "DOWN_RIGHT",
    "EMPTY",
    "LEFT",
    "RIGHT",
    "UP",
    "UP_LEFT",
    "UP_RIGHT",
    "Direction",
    "LetterGrid",
    "Placement",
    "VerificationReport",
    "WordResult",
    "WordSearch",
    "can_place",
    "fill_empty_random",
    "find_word",
    "generate_word_search",
    "place_word",
    "place_word_randomly",
    "verify_words",
]
