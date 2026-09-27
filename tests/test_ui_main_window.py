import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QSpinBox

from puzzle_portrait.config import (
    CONFIG_FILENAME,
    DEFAULT_ALLOW_PHRASES,
    DEFAULT_CELL_SIZE,
    DEFAULT_COLOR_COUNT,
    DEFAULT_FILL_EMPTY,
    DEFAULT_FONT_SIZE,
    DEFAULT_GRID_COLUMNS,
    DEFAULT_GRID_ROWS,
    DEFAULT_SEED,
    MAX_FONT_SIZE,
    MIN_FONT_SIZE,
    MOSAIC_FILENAME,
    MOSAIC_LETTERS_FILENAME,
    MOSAIC_LETTERS_SVG_FILENAME,
    MOSAIC_SVG_FILENAME,
    PREVIEW_DEBOUNCE_MS,
    WORDS_FILENAME,
    mosaic_letters_svg_filename,
)
from puzzle_portrait.render import available_font_weights
from puzzle_portrait.ui.main_window import MainWindow
from puzzle_portrait.ui.sections import HelpIcon
from puzzle_portrait.wordsearch import DIRECTIONS, FORWARD_DIRECTIONS

FIXTURE = Path(__file__).parent / "fixtures" / "sample.png"


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _flush_preview(window: MainWindow) -> None:
    window.flush_preview()
    _app().processEvents()


def test_main_window_launches_with_controls_and_preview() -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    assert window.isVisible()
    assert window.controls_panel is not None
    assert window.preview_panel is not None
    assert window.image_path.placeholderText()
    assert window.preview_placeholder.text() == "Preview will appear here"
    assert window.controls_scroll.verticalScrollBarPolicy() == (
        Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )
    assert window.new_action is not None
    assert window.open_action is not None
    assert window.save_action is not None
    assert window.save_as_action is not None
    assert window.file_button.text() == "File"
    assert window.file_button.menu() is not None
    assert not hasattr(window, "generate_button")
    assert not hasattr(window, "save_copy_action")
    assert window.main_splitter is not None
    assert window.controls_panel.minimumWidth() <= 180
    assert [section.title() for section in window.control_sections] == [
        "Image",
        "Words",
        "Crop",
        "Grid",
        "Font",
        "Placement",
    ]
    assert all(not section.is_expanded() for section in window.control_sections)
    tile_helps = [
        icon.help_text()
        for icon in window.findChildren(HelpIcon)
        if "each tile is drawn" in icon.help_text().lower()
    ]
    assert tile_helps
    assert "source photo" in tile_helps[0].lower()

    window.close()


def test_load_selected_image_displays_preview() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    app.processEvents()

    pixmap = window.preview_placeholder.pixmap()
    assert pixmap is not None
    assert not pixmap.isNull()
    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    assert window.image_path.text() == str(FIXTURE)

    window.close()


def test_browse_button_uses_file_dialog(monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(FIXTURE), "Images"),
    )
    window.browse_button.click()
    app.processEvents()

    assert window.source_image is not None
    assert window.preview_placeholder.pixmap() is not None
    assert not window.preview_placeholder.pixmap().isNull()

    window.close()


def test_preview_fits_panel_and_keeps_source_resolution() -> None:
    app = _app()
    window = MainWindow()
    window.resize(1000, 700)
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    app.processEvents()

    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    source = window.preview_placeholder.source_pixmap
    assert source.width() == DEFAULT_GRID_COLUMNS * DEFAULT_CELL_SIZE
    assert source.height() == DEFAULT_GRID_ROWS * DEFAULT_CELL_SIZE

    display = window.preview_placeholder.pixmap()
    panel = window.preview_placeholder.contentsRect().size()
    assert display is not None
    assert display.width() <= panel.width()
    assert display.height() <= panel.height()

    window.resize(640, 480)
    app.processEvents()

    assert window.source_image.size == (8, 8)
    assert window.preview_placeholder.source_pixmap.width() == (
        DEFAULT_GRID_COLUMNS * DEFAULT_CELL_SIZE
    )
    fitted = window.preview_placeholder.pixmap()
    smaller = window.preview_placeholder.contentsRect().size()
    assert fitted.width() <= smaller.width()
    assert fitted.height() <= smaller.height()

    window.close()


def test_crop_controls_update_preview_without_changing_source() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    app.processEvents()

    assert window.crop_width.value() == 8
    assert window.crop_height.value() == 8
    assert window.crop_x.value() == 0
    assert window.crop_y.value() == 0

    window.crop_width.setValue(4)
    window.crop_height.setValue(3)
    window.crop_x.setValue(2)
    window.crop_y.setValue(1)
    _flush_preview(window)

    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    assert window.preview_placeholder.source_pixmap.width() == (
        window.grid_columns.value() * window.tile_size.value()
    )
    assert window.preview_placeholder.source_pixmap.height() == (
        window.grid_rows.value() * window.tile_size.value()
    )

    window.close()


def test_grid_size_regenerates_mosaic_preview() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    app.processEvents()

    window.grid_columns.setValue(10)
    window.grid_rows.setValue(6)
    _flush_preview(window)

    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    assert window.preview_placeholder.source_pixmap.width() == 10 * window.tile_size.value()
    assert window.preview_placeholder.source_pixmap.height() == 6 * window.tile_size.value()

    window.close()


def test_tile_size_changes_render_not_logical_grid() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    app.processEvents()

    columns = window.grid_columns.value()
    rows = window.grid_rows.value()
    window.tile_size.setValue(4)
    _flush_preview(window)

    assert window.grid_columns.value() == columns
    assert window.grid_rows.value() == rows
    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    assert window.preview_placeholder.source_pixmap.width() == columns * 4
    assert window.preview_placeholder.source_pixmap.height() == rows * 4

    window.tile_size.setValue(12)
    _flush_preview(window)

    assert window.grid_columns.value() == columns
    assert window.grid_rows.value() == rows
    assert window.preview_placeholder.source_pixmap.width() == columns * 12
    assert window.preview_placeholder.source_pixmap.height() == rows * 12

    window.close()


def test_color_count_regenerates_quantized_preview(tmp_path: Path) -> None:
    colorful = Image.new("RGB", (32, 32))
    for y in range(32):
        for x in range(32):
            colorful.putpixel((x, y), ((x * 7) % 256, (y * 11) % 256, (x * y) % 256))
    path = tmp_path / "colorful.png"
    colorful.save(path)

    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    window.load_selected_image(path)
    app.processEvents()
    assert window.colors_input.currentText() == "16"
    before = window.preview_placeholder.source_pixmap.toImage()

    window.colors_input.setCurrentText("8")
    _flush_preview(window)
    after = window.preview_placeholder.source_pixmap.toImage()

    assert window.source_image is not None
    assert window.source_image.size == (32, 32)
    assert before != after

    window.close()


def test_word_list_file_fills_words_box(tmp_path: Path) -> None:
    words_file = tmp_path / "words.txt"
    words_file.write_text("cat\n\nDOG\n  bird  \n", encoding="utf-8")

    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    window.load_word_list(words_file)
    app.processEvents()

    assert window.words_path.text() == str(words_file)
    assert window.words_input.toPlainText().splitlines() == ["cat", "DOG", "bird"]

    window.close()


def test_browse_words_button_uses_file_dialog(tmp_path: Path, monkeypatch) -> None:
    words_file = tmp_path / "words.txt"
    words_file.write_text("HELLO\nWORLD\n", encoding="utf-8")

    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(words_file), "Text files"),
    )
    window.browse_words_button.click()
    app.processEvents()

    assert window.words_input.toPlainText() == "HELLO\nWORLD"

    window.close()


def _distinct_preview_font_indexes(window: MainWindow) -> tuple[int, int]:
    found: list[int] = []
    seen_files: set[str] = set()
    for index in range(window.font_input.count()):
        path = window.font_input.itemData(index)
        if not path or path in seen_files:
            continue
        seen_files.add(path)
        found.append(index)
        if len(found) == 2:
            return found[0], found[1]
    raise AssertionError("Need two system fonts with different files for preview")


def test_font_dropdown_lists_system_fonts() -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    assert window.font_input.count() > 1
    assert window.font_input.currentText()
    assert Path(window.font_input.currentData()).is_file()

    window.close()


def test_changing_font_updates_preview() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    window.grid_columns.setValue(4)
    window.grid_rows.setValue(4)
    window.tile_size.setValue(24)
    window.font_size.setValue(18)
    first, second = _distinct_preview_font_indexes(window)
    window.font_input.setCurrentIndex(first)
    _flush_preview(window)
    before = window.preview_placeholder.source_pixmap.toImage()

    window.font_input.setCurrentIndex(second)
    _flush_preview(window)
    after = window.preview_placeholder.source_pixmap.toImage()

    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    assert first != second
    assert window.font_input.itemData(first) != window.font_input.itemData(second)
    assert before != after

    window.close()


def test_font_size_spinbox_updates_preview() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    assert window.font_size.minimum() == MIN_FONT_SIZE
    assert window.font_size.maximum() == MAX_FONT_SIZE
    assert window.font_size.value() == DEFAULT_FONT_SIZE

    window.load_selected_image(FIXTURE)
    window.grid_columns.setValue(4)
    window.grid_rows.setValue(4)
    window.tile_size.setValue(24)
    window.font_size.setValue(8)
    _flush_preview(window)
    before = window.preview_placeholder.source_pixmap.toImage()

    window.font_size.setValue(28)
    _flush_preview(window)
    after = window.preview_placeholder.source_pixmap.toImage()

    assert isinstance(window.font_size, QSpinBox)
    assert window.source_image is not None
    assert window.source_image.size == (8, 8)
    assert before != after

    window.close()


def test_font_weight_and_color_mode_update_preview() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()

    assert [window.font_weight.itemText(i) for i in range(window.font_weight.count())] == [
        "Regular",
        "Medium",
        "SemiBold",
        "Bold",
    ]
    assert [window.font_color.itemText(i) for i in range(window.font_color.count())] == [
        "Automatic",
        "Black",
        "White",
        "Custom",
        "Tile shade",
    ]

    window.load_selected_image(FIXTURE)
    window.grid_columns.setValue(4)
    window.grid_rows.setValue(4)
    window.tile_size.setValue(24)
    window.font_size.setValue(18)
    window.font_color.setCurrentIndex(window.font_color.findData("black"))
    _flush_preview(window)
    before = window.preview_placeholder.source_pixmap.toImage()

    window.font_color.setCurrentIndex(window.font_color.findData("white"))
    _flush_preview(window)
    after = window.preview_placeholder.source_pixmap.toImage()

    assert window.custom_color_button.isEnabled() is False
    assert before != after

    window.font_color.setCurrentIndex(window.font_color.findData("custom"))
    app.processEvents()
    assert window.custom_color_button.isEnabled() is True

    window.close()


def test_save_project_writes_folder_and_reloads(tmp_path: Path) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT\nDOG")
    window.grid_columns.setValue(8)
    window.grid_rows.setValue(6)
    window.tile_size.setValue(10)
    window.font_size.setValue(16)
    window.font_weight.setCurrentIndex(window.font_weight.findData("bold"))
    window.font_color.setCurrentIndex(window.font_color.findData("tile_shade"))
    window.seed.setValue(11)
    window.spread_words.setChecked(True)
    window.spread_rate.setValue(2.25)
    window.allow_phrases.setChecked(True)
    window.leave_empty_blank.setChecked(True)
    window.allow_backwards.setChecked(True)
    window.balance_directions.setChecked(True)
    window.horizontal_weight.setValue(0.5)
    window.vertical_weight.setValue(2.0)
    window.diagonal_weight.setValue(1.5)
    window.crop_width.setValue(6)
    window.crop_height.setValue(5)
    window.crop_x.setValue(1)
    window.crop_y.setValue(2)
    app.processEvents()

    config_path = window.save_project_to(tmp_path)
    assert config_path == tmp_path / CONFIG_FILENAME
    assert (tmp_path / "input.png").is_file()
    assert (tmp_path / WORDS_FILENAME).read_text(encoding="utf-8") == "CAT\nDOG\n"
    assert (tmp_path / MOSAIC_FILENAME).is_file()
    assert (tmp_path / MOSAIC_LETTERS_FILENAME).is_file()
    assert "<svg" in (tmp_path / MOSAIC_SVG_FILENAME).read_text(encoding="utf-8")
    assert "<text" in (tmp_path / MOSAIC_LETTERS_SVG_FILENAME).read_text(encoding="utf-8")
    for weight in available_font_weights(window._selected_font_path()):
        weight_svg = tmp_path / mosaic_letters_svg_filename(weight)
        assert weight_svg.is_file()
        assert "<text" in weight_svg.read_text(encoding="utf-8")
    window.close()

    restored = MainWindow()
    restored.show()
    app.processEvents()
    restored.load_project_from(config_path)
    app.processEvents()
    assert restored.preview_placeholder.is_working() or (
        restored.preview_placeholder.source_pixmap is not None
        and not restored.preview_placeholder.source_pixmap.isNull()
    )
    _flush_preview(restored)

    assert restored.image_path.text() == str(tmp_path / "input.png")
    assert restored.words_input.toPlainText().splitlines() == ["CAT", "DOG"]
    assert restored.grid_columns.value() == 8
    assert restored.grid_rows.value() == 6
    assert restored.tile_size.value() == 10
    assert restored.font_size.value() == 16
    assert restored.font_weight.currentData() == "bold"
    assert restored.font_color.currentData() == "tile_shade"
    assert restored.seed.value() == 11
    assert restored.spread_words.isChecked() is True
    assert restored.spread_rate.value() == 2.25
    assert restored.allow_phrases.isChecked() is True
    assert restored.leave_empty_blank.isChecked() is True
    assert restored.allow_backwards.isChecked() is True
    assert restored.balance_directions.isChecked() is True
    assert restored.horizontal_weight.value() == 0.5
    assert restored.vertical_weight.value() == 2.0
    assert restored.diagonal_weight.value() == 1.5
    assert restored.crop_width.value() == 6
    assert restored.crop_height.value() == 5
    assert restored.crop_x.value() == 1
    assert restored.crop_y.value() == 2
    assert restored.preview_placeholder.source_pixmap is not None
    assert not restored.preview_placeholder.source_pixmap.isNull()
    restored.close()


def test_file_menu_save_and_open_use_dialogs(tmp_path: Path, monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("BIRD")
    window.seed.setValue(DEFAULT_SEED)
    app.processEvents()

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(tmp_path),
    )
    window.save_as_action.trigger()
    app.processEvents()
    assert (tmp_path / CONFIG_FILENAME).is_file()

    other = MainWindow()
    other.show()
    app.processEvents()
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(tmp_path / CONFIG_FILENAME), "Project"),
    )
    other.open_action.trigger()
    app.processEvents()

    assert other.words_input.toPlainText() == "BIRD"
    assert other.seed.value() == DEFAULT_SEED
    other.close()
    window.close()


def test_save_uses_current_folder_without_dialog(tmp_path: Path, monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    window.save_project_to(tmp_path)
    window.words_input.setPlainText("OWL")
    app.processEvents()

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Save should not ask for a folder")
        ),
    )
    window.save_action.trigger()
    app.processEvents()

    assert (tmp_path / WORDS_FILENAME).read_text(encoding="utf-8") == "OWL\n"
    window.close()


def test_save_as_asks_for_a_new_folder_even_when_a_project_exists(
    tmp_path: Path, monkeypatch
) -> None:
    current = tmp_path / "current"
    other = tmp_path / "other"
    current.mkdir()
    other.mkdir()

    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    window.save_project_to(current)
    window.words_input.setPlainText("OWL")
    app.processEvents()

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(other),
    )
    window.save_as_action.trigger()
    app.processEvents()

    assert (other / CONFIG_FILENAME).is_file()
    assert (other / WORDS_FILENAME).read_text(encoding="utf-8") == "OWL\n"
    assert window.output_dir == other
    window.close()


def test_save_waits_for_preview_workers_before_writing(tmp_path: Path, monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    app.processEvents()

    waited: list[int | None] = []
    original = window._wait_for_preview_workers

    def _track_wait(timeout_ms: int | None = None) -> None:
        waited.append(timeout_ms)
        original(timeout_ms)

    monkeypatch.setattr(window, "_wait_for_preview_workers", _track_wait)
    config_path = window.save_project_to(tmp_path)

    assert config_path == tmp_path / CONFIG_FILENAME
    assert waited
    assert window.preview_placeholder.is_working() is False
    window.close()


def test_save_reports_unexpected_errors_without_raising(
    tmp_path: Path, monkeypatch
) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    app.processEvents()

    shown: list[str] = []
    monkeypatch.setattr(
        window,
        "_combined_grid",
        lambda: (_ for _ in ()).throw(RuntimeError("disk exploded")),
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: shown.append(str(args[2] if len(args) > 2 else kwargs)),
    )

    assert window.save_project_to(tmp_path) is None
    assert shown
    assert "disk exploded" in shown[0]
    assert window.preview_placeholder.is_working() is False
    window.close()


def test_new_without_work_does_not_ask_to_save(monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()

    asked: list[int] = []
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: asked.append(1)
        or QMessageBox.StandardButton.Cancel,
    )
    window.new_action.trigger()
    app.processEvents()

    assert asked == []
    assert window.source_image is None
    assert window.preview_placeholder.text() == "Preview will appear here"
    window.close()


def test_new_discard_clears_image_words_and_preview(monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT\nDOG")
    window.grid_columns.setValue(8)
    window.allow_phrases.setChecked(True)
    window.leave_empty_blank.setChecked(True)
    window.control_sections[0].set_expanded(True)
    app.processEvents()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard,
    )
    window.new_action.trigger()
    app.processEvents()

    assert window.source_image is None
    assert window.output_dir is None
    assert window.image_path.text() == ""
    assert window.words_path.text() == ""
    assert window.words_input.toPlainText() == ""
    assert window.grid_columns.value() == DEFAULT_GRID_COLUMNS
    assert window.grid_rows.value() == DEFAULT_GRID_ROWS
    assert window.colors_input.currentText() == str(DEFAULT_COLOR_COUNT)
    assert window.allow_phrases.isChecked() is DEFAULT_ALLOW_PHRASES
    assert window.leave_empty_blank.isChecked() is (not DEFAULT_FILL_EMPTY)
    assert window.grid_columns.isEnabled() is False
    assert window.preview_placeholder.source_pixmap.isNull()
    assert window.preview_placeholder.text() == "Preview will appear here"
    assert all(not section.is_expanded() for section in window.control_sections)
    window.close()


def test_new_cancel_keeps_current_project(monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    app.processEvents()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )
    window.new_action.trigger()
    app.processEvents()

    assert window.source_image is not None
    assert window.words_input.toPlainText() == "CAT"
    window.close()


def test_new_save_writes_then_clears(tmp_path: Path, monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    app.processEvents()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(tmp_path),
    )
    window.new_action.trigger()
    app.processEvents()

    assert (tmp_path / CONFIG_FILENAME).is_file()
    assert (tmp_path / WORDS_FILENAME).read_text(encoding="utf-8") == "CAT\n"
    assert window.source_image is None
    assert window.output_dir is None
    assert window.preview_placeholder.text() == "Preview will appear here"
    window.close()


def test_new_save_cancel_keeps_current_project(monkeypatch) -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.words_input.setPlainText("CAT")
    app.processEvents()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: "",
    )
    window.new_action.trigger()
    app.processEvents()

    assert window.source_image is not None
    assert window.words_input.toPlainText() == "CAT"
    window.close()


def test_phrase_and_empty_tile_switches_change_the_grid() -> None:
    app = _app()
    window = MainWindow()
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    window.grid_columns.setValue(8)
    window.grid_rows.setValue(4)
    window.words_input.setPlainText("HI OK")
    window.leave_empty_blank.setChecked(True)
    window.allow_phrases.setChecked(False)
    app.processEvents()

    _combined, failed = window._combined_grid()
    assert failed == ("HI OK",)
    assert window._placement_directions() == FORWARD_DIRECTIONS

    window.allow_phrases.setChecked(True)
    app.processEvents()
    combined, failed = window._combined_grid()
    assert failed == ()
    letters = [
        combined[row, column].character or ""
        for row in range(4)
        for column in range(8)
    ]
    assert letters.count(" ") == 1
    assert letters.count("H") == 1
    assert letters.count("") == 32 - 5

    window.allow_backwards.setChecked(True)
    app.processEvents()
    assert window._placement_directions() == DIRECTIONS
    window.close()


def test_preview_waits_until_controls_settle() -> None:
    app = _app()
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    app.processEvents()
    window.load_selected_image(FIXTURE)
    app.processEvents()
    before = window.preview_placeholder.source_pixmap.toImage()

    window.tile_size.setValue(window.tile_size.value() + 4)
    app.processEvents()

    assert window._preview_timer.isActive()
    assert window._preview_timer.interval() == PREVIEW_DEBOUNCE_MS
    assert window.preview_placeholder.is_working()
    assert window.preview_placeholder.source_pixmap.toImage() == before

    _flush_preview(window)
    assert not window._preview_timer.isActive()
    assert not window.preview_placeholder.is_working()
    assert window.preview_placeholder.source_pixmap.toImage() != before
    window.close()
