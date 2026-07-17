"""Krita Extension: Comic Page Guides."""

from __future__ import annotations

from krita import Extension, Krita

from .guides import GuideError, apply_comic_guides
from .presets import DEFAULT_PRESET, PRESETS, ComicPreset

EXTENSION_ID = "comic_guides"
MENU_ENTRY = "Comic Page Guides"
SIMPLE_ACTION_ID = "comic_guides_standard_us"
SIMPLE_MENU_ENTRY = "Add Standard US Comic Guides"


def _qt_widgets():
    try:
        from PyQt6 import QtWidgets
    except ImportError:
        from PyQt5 import QtWidgets
    return QtWidgets


def _exec(widget):
    """Run a modal dialog (PyQt5 ``exec_`` / PyQt6 ``exec``)."""
    if hasattr(widget, "exec"):
        return widget.exec()
    return widget.exec_()


def _button_roles(QtWidgets):
    box = QtWidgets.QDialogButtonBox
    if hasattr(box, "StandardButton"):
        return box.StandardButton.Ok, box.StandardButton.Cancel
    return box.Ok, box.Cancel


def _dialog_accepted(QtWidgets, result: int) -> bool:
    code = getattr(QtWidgets.QDialog, "DialogCode", None)
    if code is not None:
        return result == code.Accepted
    return result == QtWidgets.QDialog.Accepted


class ComicGuidesDialog:
    """Compact dialog for choosing a preset and guide options."""

    def __init__(self, parent=None):
        QtWidgets = _qt_widgets()
        self._QtWidgets = QtWidgets
        self._dialog = QtWidgets.QDialog(parent)
        self._dialog.setWindowTitle("Comic Page Guides")
        self._dialog.setMinimumWidth(420)

        layout = QtWidgets.QVBoxLayout(self._dialog)

        form = QtWidgets.QFormLayout()
        self._preset_combo = QtWidgets.QComboBox()
        for name in PRESETS:
            self._preset_combo.addItem(name)
        form.addRow("Document preset:", self._preset_combo)

        form.addRow("Units:", QtWidgets.QLabel("Inches"))

        self._vertical_edit = QtWidgets.QLineEdit()
        self._vertical_edit.setReadOnly(True)
        form.addRow("Vertical guides:", self._vertical_edit)

        self._horizontal_edit = QtWidgets.QLineEdit()
        self._horizontal_edit.setReadOnly(True)
        form.addRow("Horizontal guides:", self._horizontal_edit)

        layout.addLayout(form)

        self._replace = QtWidgets.QCheckBox("Replace existing guides")
        self._replace.setChecked(True)
        self._show = QtWidgets.QCheckBox("Show guides")
        self._show.setChecked(True)
        self._lock = QtWidgets.QCheckBox("Lock guides")
        self._lock.setChecked(True)
        self._snap = QtWidgets.QCheckBox("Snap to guides")
        self._snap.setChecked(True)
        self._nine_panel = QtWidgets.QCheckBox(
            "Add 9-panel grid (orange vector layer in safe area)"
        )
        self._nine_panel.setChecked(True)
        for box in (
            self._replace,
            self._show,
            self._lock,
            self._snap,
            self._nine_panel,
        ):
            layout.addWidget(box)

        ok_role, cancel_role = _button_roles(QtWidgets)
        buttons = QtWidgets.QDialogButtonBox(ok_role | cancel_role)
        ok_button = buttons.button(ok_role)
        if ok_button is not None:
            ok_button.setText("Create Guides")
        buttons.accepted.connect(self._dialog.accept)
        buttons.rejected.connect(self._dialog.reject)
        layout.addWidget(buttons)

        self._preset_combo.currentIndexChanged.connect(self._refresh_guide_fields)
        self._refresh_guide_fields()

    def _selected_preset(self) -> ComicPreset:
        return PRESETS[self._preset_combo.currentText()]

    @staticmethod
    def _format_inches(values: tuple[float, ...]) -> str:
        return ", ".join(f"{v:.4f}".rstrip("0").rstrip(".") for v in values)

    def _refresh_guide_fields(self) -> None:
        preset = self._selected_preset()
        self._vertical_edit.setText(self._format_inches(preset.vertical_in))
        self._horizontal_edit.setText(self._format_inches(preset.horizontal_in))

    def run(self) -> bool:
        return _dialog_accepted(self._QtWidgets, _exec(self._dialog))

    def options(self) -> dict:
        return {
            "preset": self._selected_preset(),
            "replace": self._replace.isChecked(),
            "visible": self._show.isChecked(),
            "locked": self._lock.isChecked(),
            "snap": self._snap.isChecked(),
            "nine_panel": self._nine_panel.isChecked(),
        }


class ComicGuidesExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(EXTENSION_ID, MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.open_dialog)

        simple = window.createAction(
            SIMPLE_ACTION_ID, SIMPLE_MENU_ENTRY, "tools/scripts"
        )
        simple.triggered.connect(self.add_standard_guides)

    def _active_document(self):
        return Krita.instance().activeDocument()

    def _show_message(self, title: str, text: str, *, error: bool = False) -> None:
        QtWidgets = _qt_widgets()
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        if hasattr(QtWidgets.QMessageBox, "Icon"):
            msg.setIcon(
                QtWidgets.QMessageBox.Icon.Critical
                if error
                else QtWidgets.QMessageBox.Icon.Information
            )
        else:
            msg.setIcon(
                QtWidgets.QMessageBox.Critical
                if error
                else QtWidgets.QMessageBox.Information
            )
        _exec(msg)

    def open_dialog(self) -> None:
        document = self._active_document()
        if document is None:
            self._show_message(
                "Comic Page Guides",
                "No active document. Open or create a page first.",
                error=True,
            )
            return

        dialog = ComicGuidesDialog()
        if not dialog.run():
            return

        opts = dialog.options()
        try:
            message = apply_comic_guides(
                document,
                opts["preset"],
                replace=opts["replace"],
                visible=opts["visible"],
                locked=opts["locked"],
                snap=opts["snap"],
                nine_panel=opts["nine_panel"],
            )
        except GuideError as exc:
            self._show_message("Comic Page Guides", str(exc), error=True)
            return

        self._show_message("Comic Page Guides", message)

    def add_standard_guides(self) -> None:
        try:
            message = apply_comic_guides(
                self._active_document(), DEFAULT_PRESET, replace=True
            )
        except GuideError as exc:
            self._show_message("Comic Page Guides", str(exc), error=True)
            return
        self._show_message("Comic Page Guides", message)
