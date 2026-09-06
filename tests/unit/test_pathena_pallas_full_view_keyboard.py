from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from athena.desktop.pathena_pallas_field import PallasGroundedFieldController
from athena.desktop.pathena_pallas_full_view import PallasFullViewController


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


def _controller(qapp: QApplication) -> tuple[QWidget, PallasFullViewController]:
    window = QWidget()
    window.resize(900, 640)
    layout = QVBoxLayout(window)
    target = QWidget(window)
    target.setObjectName("pallasVisualPlaceholder")
    layout.addWidget(target)
    grounded = PallasGroundedFieldController(window, None)
    controller = PallasFullViewController(window, grounded)
    window.show()
    qapp.processEvents()
    grounded.field.canvas.setFocus()
    qapp.processEvents()
    return window, controller


def test_ctrl_enter_opens_full_workspace_without_stealing_plain_enter(
    qapp: QApplication,
) -> None:
    window, controller = _controller(qapp)
    canvas = controller._grounded_controller.field.canvas
    try:
        QTest.keyClick(canvas, Qt.Key.Key_Return)
        qapp.processEvents()
        assert controller.dialog is None

        QTest.keyClick(canvas, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier)
        qapp.processEvents()
        assert controller.dialog is not None
        assert controller.workspace is not None
        assert controller.dialog.isVisible()
        assert controller.workspace.field.canvas.hasFocus()
    finally:
        controller.dispose()
        window.close()
        window.deleteLater()


def test_full_view_accessibility_copy_exposes_keyboard_path(qapp: QApplication) -> None:
    window, controller = _controller(qapp)
    target = controller._grounded_controller.target
    canvas = controller._grounded_controller.field.canvas
    try:
        assert "Ctrl+Enter" in target.toolTip()
        assert "Ctrl+Enter" in target.accessibleDescription()
        assert "Ctrl+Enter" in canvas.toolTip()
    finally:
        controller.dispose()
        window.close()
        window.deleteLater()
