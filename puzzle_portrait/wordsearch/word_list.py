"""Parse word-list lines, including optional pinned start cells."""

from __future__ import annotations

import re
from dataclasses import dataclass

from puzzle_portrait.wordsearch.directions import DOWN, DOWN_RIGHT, RIGHT, UP_RIGHT, Direction

PINNED_DIRECTIONS: dict[str, Direction] = {
    "HOR": RIGHT,
    "VER": DOWN,
    "DIAG_LB_RU": UP_RIGHT,
    "DIAG_LU_RB": DOWN_RIGHT,
}

_CONSTRAINT = re.compile(
    r"^(?P<text>.*?)\s*"
    r"\{\{\s*(?P<row>-?\d+)\s*,\s*(?P<col>-?\d+)\s*\}\s*,\s*"
    r"(?P<direction>[A-Za-z_]+)\s*\}\s*$"
)


@dataclass(frozen=True, slots=True)
class WordSpec:
    """One word-list entry, optionally pinned to a cell and direction."""

    word: str
    row: int | None = None
    column: int | None = None
    direction: Direction | None = None
    source: str = ""

    def is_pinned(self) -> bool:
        return self.direction is not None


def parse_word_line(line: str) -> WordSpec:
    """Read a word or phrase and an optional ``{{row, col}, DIRECTION}`` pin.

    ``row`` and ``column`` are 0-based from the top-left cell. ``DIRECTION`` is
    one of HOR, VER, DIAG_LB_RU, or DIAG_LU_RB.
    """
    source = line.strip()
    if not source:
        raise ValueError("Word line is empty")

    match = _CONSTRAINT.fullmatch(source)
    if match:
        text = match.group("text").strip()
        if not text:
            raise ValueError("Pinned line is missing a word")
        name = match.group("direction").upper()
        direction = PINNED_DIRECTIONS.get(name)
        if direction is None:
            raise ValueError(f"Unknown direction {match.group('direction')!r}")
        return WordSpec(
            word=text,
            row=int(match.group("row")),
            column=int(match.group("col")),
            direction=direction,
            source=source,
        )

    if "{{" in source:
        raise ValueError(f"Invalid placement constraint: {source}")
    return WordSpec(word=source, source=source)
