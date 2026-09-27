"""Launch the Puzzle Portrait desktop application."""

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from puzzle_portrait.ui.main_window import MainWindow


def _install_excepthook() -> None:
    def _hook(exc_type, exc, tb):
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        sys.stderr.write(text)
        try:
            QMessageBox.critical(None, "Puzzle Portrait error", text[-4000:])
        except Exception:
            pass

    sys.excepthook = _hook


def main(argv: list[str] | None = None) -> int:
    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    _install_excepthook()
    window = MainWindow()
    window.show()
    return app.exec()
