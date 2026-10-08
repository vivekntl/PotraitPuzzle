import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel, QToolTip

from puzzle_portrait.config import HELP_HOVER_DELAY_MS
from puzzle_portrait.ui.sections import (
    CollapsibleSection,
    HelpIcon,
    checkbox_with_help,
    labeled_field,
)


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_section_starts_collapsed_and_can_expand() -> None:
    _app()
    section = CollapsibleSection("Crop")
    inner = QLabel("Width")
    section.add_widget(inner)

    assert section.title() == "Crop"
    assert section.is_expanded() is False
    assert section._body.isHidden() is True

    section.set_expanded(True)
    assert section.is_expanded() is True
    assert section._body.isHidden() is False
    section.set_title("Could not place (2)")
    assert section.title() == "Could not place (2)"


def test_labeled_field_puts_title_above_the_control() -> None:
    _app()
    control = QLabel("value")
    field = labeled_field("Width", control, "How wide the crop is.")
    labels = field.findChildren(QLabel)
    titles = [label.text() for label in labels]

    assert "Width" in titles
    icons = [child for child in field.findChildren(HelpIcon)]
    assert len(icons) == 1
    assert "crop" in icons[0].help_text().lower()


def test_help_icon_waits_before_showing_and_cancels_on_leave() -> None:
    app = _app()
    icon = HelpIcon("Tile size only changes the drawing size.", delay_ms=800)
    icon.show()
    app.processEvents()

    icon.enterEvent(
        QEnterEvent(QPointF(2, 2), QPointF(2, 2), QPointF(2, 2))
    )
    app.processEvents()
    assert icon._timer.isActive()
    assert icon._timer.interval() == 800
    assert QToolTip.isVisible() is False

    icon.leaveEvent(QEvent(QEvent.Type.Leave))
    app.processEvents()
    assert icon._timer.isActive() is False
    assert QToolTip.isVisible() is False
    icon.close()


def test_checkbox_with_help_keeps_the_checkbox() -> None:
    _app()
    box = QCheckBox("Leave empty tiles blank")
    row = checkbox_with_help(box, "Unused tiles stay empty.")
    icons = row.findChildren(HelpIcon)

    assert box in row.findChildren(QCheckBox)
    assert len(icons) == 1
    assert icons[0].help_text() == "Unused tiles stay empty."


def test_help_hover_delay_is_not_instant() -> None:
    assert HELP_HOVER_DELAY_MS >= 500
