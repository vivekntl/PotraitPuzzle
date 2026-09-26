"""RGB background color for a mosaic cell."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RGB:
    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        for name, value in (
            ("red", self.red),
            ("green", self.green),
            ("blue", self.blue),
        ):
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be in 0..255, got {value}")
