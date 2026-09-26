# Puzzle Portrait

A Python tool that turns a portrait into a word-search mosaic: the image is sampled onto a letter grid, words are placed through that grid, and the result is exported as a printable puzzle.

This repository currently contains only the project layout. No generation logic has been implemented yet.

## Requirements

- Python 3.12 or later
- A virtual environment (recommended)

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Tests

```powershell
pytest
```

## Project layout

```
puzzle_portrait/     application package
  config/            settings and defaults
  image/             load and process the source portrait
  grid/              letter-grid data structures
  wordsearch/        word placement and puzzle generation
  render/            visual composition of the mosaic
  export/            output formats (image, PDF, etc.)
tests/               unit and integration tests
```

## Usage

Print width, height, color mode, and aspect ratio for an image (the file is not modified):

```powershell
python -m puzzle_portrait info path\to\portrait.png
```

Crop a photograph to a centered square, resize it to 100×100, and save a full-color preview plus a quantized comparison image under `output/`:

```powershell
python -m puzzle_portrait preview path\to\portrait.png
python -m puzzle_portrait preview path\to\portrait.png --colors 24
```

Supported `--colors` values: 8, 16, 24, 32, 48 (default: 16).

Render a color-cell mosaic PNG (no letters yet). Cell size is configurable; `--grid-lines` adds a subtle divider:

```powershell
python -m puzzle_portrait render path\to\portrait.png
python -m puzzle_portrait render path\to\portrait.png --cell-size 12 --grid-lines --colors 24
```

Build two mosaics from a photo and a word list: color tiles only, then the same tiles with letters:

```powershell
python -m puzzle_portrait mosaic path\to\portrait.png CAT DOG BIRD --grid-lines
```
