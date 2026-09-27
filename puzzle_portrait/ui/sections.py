"""Collapsible control groups, stacked fields, and delayed help icons."""

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from puzzle_portrait.config import HELP_HOVER_DELAY_MS


class HelpIcon(QLabel):
    """A small ? that shows help only after the pointer rests on it."""

    def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        delay_ms: int = HELP_HOVER_DELAY_MS,
    ) -> None:
        super().__init__("?", parent)
        self._text = text
        self._delay_ms = delay_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_help)
        self.setObjectName("helpIcon")
        self.setFixedSize(18, 18)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.setStyleSheet(
            "QLabel#helpIcon {"
            " color: #444;"
            " border: 1px solid #888;"
            " border-radius: 9px;"
            " font-size: 11px;"
            " font-weight: bold;"
            "}"
        )

    def help_text(self) -> str:
        return self._text

    def enterEvent(self, event) -> None:
        self._timer.start(self._delay_ms)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._timer.stop()
        QToolTip.hideText()
        super().leaveEvent(event)

    def _show_help(self) -> None:
        if not self.underMouse():
            return
        if QApplication.activeModalWidget() is not None:
            return
        QToolTip.showText(QCursor.pos() + QPoint(12, 12), self._text, self)


class CollapsibleSection(QWidget):
    """A titled group that starts collapsed and can be opened in place."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("collapsibleSection")
        self._toggle = QToolButton(self)
        self._toggle.setObjectName("sectionToggle")
        self._toggle.setText(title)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(False)
        self._toggle.setAutoRaise(False)
        self._toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle.setArrowType(Qt.ArrowType.RightArrow)
        self._toggle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._toggle.toggled.connect(self._on_toggled)

        self._body = QWidget()
        self._body.setVisible(False)
        self.body_layout = QVBoxLayout(self._body)
        self.body_layout.setContentsMargins(8, 4, 0, 8)
        self.body_layout.setSpacing(8)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(0)
        layout.addWidget(self._toggle)
        layout.addWidget(self._body)

    def title(self) -> str:
        return self._toggle.text()

    def is_expanded(self) -> bool:
        return self._toggle.isChecked()

    def set_expanded(self, expanded: bool) -> None:
        self._toggle.setChecked(expanded)

    def add_widget(self, widget: QWidget) -> None:
        self.body_layout.addWidget(widget)

    def _on_toggled(self, expanded: bool) -> None:
        self._toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        self._body.setVisible(expanded)


def labeled_field(title: str, widget: QWidget, help_text: str) -> QWidget:
    """Put a wrapping label and delayed-help icon above a stretching control."""
    host = QWidget()
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    header = QWidget()
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(6)
    label = QLabel(title)
    label.setObjectName("fieldLabel")
    label.setWordWrap(True)
    header_layout.addWidget(label, 1)
    header_layout.addWidget(HelpIcon(help_text), 0, Qt.AlignmentFlag.AlignTop)

    stretch_control(widget)
    layout.addWidget(header)
    layout.addWidget(widget)
    return host


def checkbox_with_help(checkbox: QCheckBox, help_text: str) -> QWidget:
    """Put a delayed-help icon to the right of a checkbox."""
    host = QWidget()
    layout = QHBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(checkbox, 1)
    layout.addWidget(HelpIcon(help_text), 0, Qt.AlignmentFlag.AlignTop)
    return host


def stretch_control(widget: QWidget) -> None:
    """Let a control shrink and grow with the left panel width."""
    widget.setMinimumWidth(0)
    policy = widget.sizePolicy()
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, policy.verticalPolicy())
