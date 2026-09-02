from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_inspector_responsiveness_5200 import (
    InspectorResponsivenessController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _window() -> tuple[QWidget, QWidget]:
    window = QWidget()
    inspector = QWidget(window)
    inspector.setObjectName("inspector")
    return window, inspector


def test_inspector_width_protects_central_workspace_by_window_size() -> None:
    _app()
    window, inspector = _window()
    window.resize(1320, 780)

    controller = InspectorResponsivenessController(window)

    assert inspector.width() == 300
    assert inspector.property("pathenaInspectorWidthMode") == "compact"
    assert inspector.property("pathenaCentralWorkspaceProtected") is True

    window.resize(1520, 900)
    controller.sync()
    assert inspector.width() == 340
    assert inspector.property("pathenaInspectorWidthMode") == "comfortable"

    window.resize(1660, 980)
    controller.sync()
    assert inspector.width() == 388
    assert inspector.property("pathenaInspectorWidthMode") == "wide"


def test_inspector_resize_does_not_change_existing_visibility() -> None:
    _app()
    window, inspector = _window()
    inspector.hide()
    window.resize(1320, 780)

    controller = InspectorResponsivenessController(window)

    assert inspector.width() == 300
    assert inspector.isHidden()
    assert controller.parent() is window
