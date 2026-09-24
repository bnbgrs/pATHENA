from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QToolButton

from athena.desktop.pathena_v3_shell import install_v3_shell
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v3_primary_navigation_is_labeled_and_debug_markers_are_absent() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        shell = install_v3_shell(window)

        buttons = shell.shell.findChildren(QToolButton, "v3NavButton")
        labels = {button.text() for button in buttons}
        assert {"Chat", "Knowledge", "Research", "Jobs", "Sources", "PALLAS", "System", "Settings"} <= labels

        assert shell.shell.findChild(QLabel, "v3BuildMark") is None
        scope = shell.shell.findChild(QLabel, "v3RuntimeScope")
        assert scope is not None
        assert scope.text() == "LOCAL"
        assert shell.shell.findChild(QLabel, "v3RuntimeDot") is None
    finally:
        window.close()


def test_v3_inspector_never_opens_just_because_context_becomes_available() -> None:
    app = _app()
    window = PathenaMainWindow()
    try:
        shell = install_v3_shell(window)
        window.show()
        app.processEvents()

        inspector = window.findChild(QFrame, "inspector")
        assert inspector is not None
        assert not inspector.isVisible()

        window._set_context_available(True)
        app.processEvents()
        assert not inspector.isVisible()

        shell._inspector_button.click()
        app.processEvents()
        assert shell._inspector_button.isChecked()
        assert inspector.isVisible()

        window.navigation.setCurrentRow(1)
        app.processEvents()
        assert not inspector.isVisible()
        assert not shell._inspector_button.isChecked()
        assert shell._inspector_button.isHidden()
    finally:
        window.close()


def test_v3_stylesheet_has_explicit_navigation_and_inspector_states() -> None:
    stylesheet = PATHENA_V3_STYLESHEET
    assert 'QToolButton[v3Nav="true"]' in stylesheet
    assert "QPushButton#v3InspectorButton:checked" in stylesheet
    assert "QLabel#v3RuntimeScope" in stylesheet
    assert "QLabel#v3RuntimeDot" not in stylesheet
