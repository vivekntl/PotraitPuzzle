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

Crop a photograph to a centered square, resize it to 100×100, and save it under `output/`:

```powershell
python -m puzzle_portrait preview path\to\portrait.png
```
