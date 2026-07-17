from krita import Extension

from .guides import GuideError, apply_comic_guides, create_comic_document
from .presets import DEFAULT_PRESET

EXTENSION_ID = "comic_guides_new_page"
MENU_ENTRY = "New US Comic Page (11×17)"


def _qt_widgets():
    try:
        from PyQt6 import QtWidgets
    except ImportError:
        from PyQt5 import QtWidgets
    return QtWidgets


def _exec(widget):
    if hasattr(widget, "exec"):
        return widget.exec()
    return widget.exec_()


class ComicGuidesExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(EXTENSION_ID, MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.new_comic_page)

    def _show_error(self, text: str) -> None:
        QtWidgets = _qt_widgets()
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(MENU_ENTRY)
        msg.setText(text)
        if hasattr(QtWidgets.QMessageBox, "Icon"):
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        else:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        _exec(msg)

    def new_comic_page(self) -> None:
        try:
            document = create_comic_document(DEFAULT_PRESET)
            apply_comic_guides(
                document,
                DEFAULT_PRESET,
                replace=True,
                visible=True,
                locked=True,
                snap=True,
                nine_panel=True,
            )
        except GuideError as exc:
            self._show_error(str(exc))
