import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

from puzzle_portrait.ui.preview import FitPreview


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_cell_at_maps_widget_point_to_row_and_column() -> None:
    app = _app()
    preview = FitPreview()
    preview.resize(420, 260)
    preview.show()
    app.processEvents()
    preview.set_source_image(
        Image.new("RGB", (80, 40), (40, 40, 40)),
        columns=8,
        rows=4,
    )
    app.processEvents()

    rect = preview._pixmap_rect()
    assert rect.width() > 0
    assert rect.height() > 0
    assert preview.cell_at(rect.topLeft()) == (0, 0)

    cell_w = rect.width() / 8
    cell_h = rect.height() / 4
    last = QPoint(
        rect.x() + int(cell_w * 7.5),
        rect.y() + int(cell_h * 3.5),
    )
    assert preview.cell_at(last) == (3, 7)
    assert preview.cell_at(QPoint(rect.x() - 2, rect.y() - 2)) is None
    preview.close()


def test_cell_hover_label_shows_row_and_column() -> None:
    app = _app()
    preview = FitPreview()
    preview.resize(420, 260)
    preview.show()
    app.processEvents()
    preview.set_source_image(
        Image.new("RGB", (80, 40), (40, 40, 40)),
        columns=8,
        rows=4,
    )
    preview.set_show_cell_hover(True)
    app.processEvents()

    rect = preview._pixmap_rect()
    preview._update_hover(rect.topLeft())
    app.processEvents()

    assert preview.shows_cell_hover() is True
    assert preview._hover_label.isVisible()
    assert preview._hover_label.text() == "0, 0"

    preview.set_show_cell_hover(False)
    assert preview._hover_label.isVisible() is False
    preview.close()
