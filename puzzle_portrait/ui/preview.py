"""Convert and display images in the preview panel without altering the source."""

from PIL.Image import Image as PILImage
from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QResizeEvent
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

    def clear_preview(self) -> None:
        self._source = QPixmap()
        self.setPixmap(QPixmap())
        self.setText(self._placeholder)
        self.set_working(False)

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

    def set_source_image(self, image: PILImage) -> None:
        self._source = pil_to_qpixmap(image)
        self.setText("")
        self._fit_to_panel()
        self._working.setGeometry(self.rect())
        self._working.raise_()

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
