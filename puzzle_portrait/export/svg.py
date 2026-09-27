"""Save SVG documents to the filesystem."""

from pathlib import Path


def save_svg(svg: str, path: str | Path) -> Path:
    """Write ``svg`` text to ``path``, creating parent directories as needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    return output_path
