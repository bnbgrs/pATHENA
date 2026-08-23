from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QWidget

from athena.desktop.pathena_dialog_focus_return_7200 import DialogFocusReturnController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QApplication, QWidget, QLineEdit, QPushButton, QDialog]:
    app = _app()
    window = QWidget()
    previous = QLineEdit(window)
    newer = QPushButton("New target", window)
    dialog = QDialog(window)
    window.resize(320, 180)
    window.show()
    app.processEvents()
    return app, window, previous, newer, dialog


def test_capture_remembers_pre_dialog_focus() -> None:
    app, window, previous, _newer, dialog = _surface()
    controller = DialogFocusReturnController(window)
    previous.setFocus()
    app.processEvents()

    controller._capture(dialog)

    assert controller._previous[dialog] is previous
    assert dialog.property("pathenaFocusReturnCaptured") is True


def test_close_restores_previous_focus_when_unclaimed() -> None:
    app, window, previous, _newer, _dialog = _surface()
    controller = DialogFocusReturnController(window)
    previous.setFocus()
    app.processEvents()

    controller._restore_if_unclaimed(previous)
    app.processEvents()

    assert QApplication.focusWidget() is previous
    assert previous.property("pathenaDialogFocusReturn") == "restored"


def test_newer_valid_focus_is_not_stolen() -> None:
    app, window, previous, newer, _dialog = _surface()
    controller = DialogFocusReturnController(window)
    newer.setFocus()
    app.processEvents()

    controller._restore_if_unclaimed(previous)
    app.processEvents()

    assert QApplication.focusWidget() is newer
    assert previous.property("pathenaDialogFocusReturn") == "preserved-newer-focus"


def test_no_focus_restore_to_nofocus_widget() -> None:
    app, window, previous, newer, _dialog = _surface()
    controller = DialogFocusReturnController(window)
    previous.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    newer.setFocus()
    app.processEvents()

    controller._restore_if_unclaimed(previous)

    assert QApplication.focusWidget() is newer
