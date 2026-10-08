"""Convert and display images in the preview panel without altering the source."""

from PIL.Image import Image as PILImage
from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPen, QPixmap, QResizeEvent
from PySide6.QtWidgets import QFrame, QLabel, QWidget


def pil_to_qpixmap(image: PILImage) -> QPixmap:
    """Copy a Pillow image into a QPixmap without changing the source."""
    rgb = image.convert("RGB")
    qimage = QImage(
        rgb.tobytes(),
        rgb.width,
        rgb.height,
        rgb.width * 3,
        QImage.Format.Format_RGB888,
    )
    return QPixmap.fromImage(qimage.copy())


class WorkingOverlay(QWidget):
    """Dim the preview and spin a simple indicator while a job is running."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._advance)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def start(self) -> None:
        self.show()
        self.raise_()
        if not self._timer.isActive():
            self._timer.start()
        self.update()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def is_working(self) -> bool:
        return self.isVisible()

    def _advance(self) -> None:
        self._angle = (self._angle + 18) % 360
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(16, 16, 16, 100))

        size = max(36, min(self.width(), self.height()) // 8)
        arc = QRect(
            (self.width() - size) // 2,
            (self.height() - size) // 2 - 16,
            size,
            size,
        )
        pen = QPen(QColor(255, 255, 255, 230))
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(arc, self._angle * 16, 110 * 16)

        painter.setPen(QColor(255, 255, 255))
        painter.drawText(
            self.rect().adjusted(0, size // 2 + 8, 0, 0),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "Working…",
        )


class FitPreview(QLabel):
    """Show an image scaled to this widget, keeping aspect ratio."""

    def __init__(self, placeholder: str = "Preview will appear here") -> None:
        super().__init__(placeholder)
        self._placeholder = placeholder
        self._source = QPixmap()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(360, 360)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("previewPlaceholder")
        self._working = WorkingOverlay(self)
        self._columns = 0
        self._rows = 0
        self._show_cell_hover = False
        self._hover_label = QLabel(self)
        self._hover_label.setObjectName("cellHoverLabel")
        self._hover_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._hover_label.setStyleSheet(
            "QLabel#cellHoverLabel {"
            " background: rgba(20, 20, 20, 210);"
            " color: white;"
            " padding: 2px 8px;"
            " border-radius: 4px;"
            " font-size: 12px;"
            "}"
        )
        self._hover_label.hide()

    def clear_preview(self) -> None:
        self._source = QPixmap()
        self._columns = 0
        self._rows = 0
        self.setPixmap(QPixmap())
        self.setText(self._placeholder)
        self.set_working(False)
        self._hover_label.hide()

    @property
    def source_pixmap(self) -> QPixmap:
        return self._source

    def is_working(self) -> bool:
        return self._working.is_working()

    def set_working(self, working: bool) -> None:
        if working:
            self._working.setGeometry(self.rect())
            self._working.start()
        else:
            self._working.stop()

    def set_show_cell_hover(self, enabled: bool) -> None:
        self._show_cell_hover = enabled
        self.setMouseTracking(enabled)
        if not enabled:
            self._hover_label.hide()

    def shows_cell_hover(self) -> bool:
        return self._show_cell_hover

    def set_source_image(
        self,
        image: PILImage,
        *,
        columns: int,
        rows: int,
    ) -> None:
        self._source = pil_to_qpixmap(image)
        self._columns = max(0, columns)
        self._rows = max(0, rows)
        self.setText("")
        self._fit_to_panel()
        self._working.setGeometry(self.rect())
        self._working.raise_()
        self._hover_label.hide()

    def cell_at(self, pos: QPoint) -> tuple[int, int] | None:
        """Return ``(row, column)`` for a widget position, or None if off-grid."""
        if self._columns < 1 or self._rows < 1 or self._source.isNull():
            return None
        rect = self._pixmap_rect()
        if rect.width() < 1 or rect.height() < 1:
            return None
        local_x = pos.x() - rect.x()
        local_y = pos.y() - rect.y()
        if local_x < 0 or local_y < 0 or local_x >= rect.width() or local_y >= rect.height():
            return None
        column = min(self._columns - 1, int(local_x * self._columns / rect.width()))
        row = min(self._rows - 1, int(local_y * self._rows / rect.height()))
        return row, column

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._update_hover(event.position().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover_label.hide()
        super().leaveEvent(event)

    def _update_hover(self, pos: QPoint) -> None:
        if not self._show_cell_hover:
            self._hover_label.hide()
            return
        cell = self.cell_at(pos)
        if cell is None:
            self._hover_label.hide()
            return
        row, column = cell
        self._hover_label.setText(f"{row}, {column}")
        self._hover_label.adjustSize()
        x = min(pos.x() + 12, max(0, self.width() - self._hover_label.width()))
        y = min(pos.y() + 12, max(0, self.height() - self._hover_label.height()))
        self._hover_label.move(x, y)
        self._hover_label.show()
        self._hover_label.raise_()

    def _pixmap_rect(self) -> QRect:
        pixmap = self.pixmap()
        if pixmap is None or pixmap.isNull():
            return QRect()
        area = self.contentsRect()
        x = area.x() + (area.width() - pixmap.width()) // 2
        y = area.y() + (area.height() - pixmap.height()) // 2
        return QRect(x, y, pixmap.width(), pixmap.height())

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._working.setGeometry(self.rect())
        self._fit_to_panel()

    def _fit_to_panel(self) -> None:
        if self._source.isNull():
            return
        area = self.contentsRect().size()
        if area.width() < 1 or area.height() < 1:
            return
        self.setPixmap(
            self._source.scaled(
                area,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
