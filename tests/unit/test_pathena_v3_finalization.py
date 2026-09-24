from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QToolButton

from athena.desktop.pathena_v3_shell import install_v3_shell
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET, V3_SURFACE, V3_TEXT_DIM
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
        assert shell._inspector_button.isHidden()

        window._set_context_available(True)
        app.processEvents()
        assert not inspector.isVisible()
        assert shell._inspector_button.isVisible()

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
    assert "QToolButton[v3Nav=\"true\"]:focus" in stylesheet
    assert "QPushButton#sendButton:focus" in stylesheet
    assert "QWidget#v3SystemWorkspace" in stylesheet
    assert "QTabWidget#systemOperationsTabs::pane" in stylesheet
    assert "QDialog#helpWorkspace" in stylesheet
    assert "QFrame#helpCapabilityRow" in stylesheet
    assert "QLabel#v3RuntimeScope" in stylesheet
    assert "QLabel#v3RuntimeDot" not in stylesheet


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linear(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_v3_secondary_text_remains_readable_on_raised_surfaces() -> None:
    assert _contrast_ratio(V3_TEXT_DIM, V3_SURFACE) >= 4.5
