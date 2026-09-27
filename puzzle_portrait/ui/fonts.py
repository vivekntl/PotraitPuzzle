"""Find system font files that Pillow can load."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

_FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}


def font_directories() -> list[Path]:
    directories: list[Path] = []
    if sys.platform == "win32":
        windows = Path(os.environ.get("WINDIR", r"C:\Windows"))
        directories.append(windows / "Fonts")
        local = os.environ.get("LOCALAPPDATA")
        if local:
            directories.append(Path(local) / "Microsoft" / "Windows" / "Fonts")
    elif sys.platform == "darwin":
        directories.extend(
            (
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            )
        )
    else:
        directories.extend(
            (
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".local" / "share" / "fonts",
                Path.home() / ".fonts",
            )
        )
    return [path for path in directories if path.is_dir()]


_STYLE_SUFFIXES = (
    " bold",
    " italic",
    " bold italic",
    " light",
    " thin",
    " medium",
    " semibold",
    " demi bold",
    " demibold",
    " heavy",
    " condensed",
    " narrow",
    " oblique",
    " regular",
)


def list_system_fonts(*, regular_only: bool = False) -> list[tuple[str, Path]]:
    """Return unique ``(display name, file path)`` pairs, sorted by name."""
    fonts: list[tuple[str, Path]] = []
    seen: set[str] = set()

    for family, path in _named_font_files():
        if regular_only and _is_style_variant(family):
            continue
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        fonts.append((family, path))

    fonts.sort(key=lambda item: item[0].casefold())
    return fonts


def _is_style_variant(name: str) -> bool:
    lower = f" {name.casefold()} "
    return any(lower.endswith(f"{suffix} ") for suffix in _STYLE_SUFFIXES)


def font_file_for_family(family: str) -> Path | None:
    """Return a .ttf/.otf/.ttc path for ``family``, or None if none is found."""
    if not family.strip():
        return None

    key = family.strip().casefold()
    for name, path in list_system_fonts():
        if name.casefold() == key:
            return path

    compact = key.replace(" ", "")
    exact: Path | None = None
    prefix: Path | None = None
    for _, path in list_system_fonts():
        stem = path.stem.casefold().replace(" ", "")
        if stem == compact:
            exact = path
            break
        if prefix is None and (stem.startswith(compact) or compact.startswith(stem)):
            prefix = path
    return exact or prefix


def _named_font_files() -> list[tuple[str, Path]]:
    named = list(_windows_registry_fonts())
    known = {str(path.resolve()) for _, path in named}
    for directory in font_directories():
        for path in directory.iterdir():
            if path.suffix.lower() not in _FONT_SUFFIXES or not path.is_file():
                continue
            if str(path.resolve()) in known:
                continue
            named.append((path.stem, path))
    return named


@lru_cache(maxsize=1)
def _windows_registry_fonts() -> tuple[tuple[str, Path], ...]:
    if sys.platform != "win32":
        return ()

    import winreg

    found: list[tuple[str, Path]] = []
    fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    locations = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
    )
    for hive, subkey in locations:
        try:
            handle = winreg.OpenKey(hive, subkey)
        except OSError:
            continue
        index = 0
        while True:
            try:
                display_name, filename, _ = winreg.EnumValue(handle, index)
            except OSError:
                break
            index += 1
            if not isinstance(filename, str):
                continue
            path = Path(filename)
            if not path.is_absolute():
                path = fonts_dir / filename
            if path.suffix.lower() not in _FONT_SUFFIXES or not path.is_file():
                continue
            found.append((_family_from_registry_name(display_name), path))
        winreg.CloseKey(handle)
    return tuple(found)


def _family_from_registry_name(name: str) -> str:
    cut = name.rfind(" (")
    if cut != -1 and name.endswith(")"):
        return name[:cut]
    return name
