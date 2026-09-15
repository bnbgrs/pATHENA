from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QFrame, QScrollArea, QWidget

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_reference_backgrounds import stabilize_reference_backgrounds


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_reference_backgrounds_paint_workspace_inspector_and_scroll_viewport() -> None:
    app = _app()
    window = QWidget()
    knowledge = QWidget(window)
    knowledge.setObjectName("knowledgeWorkspace")
    inspector = QFrame(window)
    inspector.setObjectName("inspector")
    chat_scroll = QScrollArea(window)
    chat_scroll.setObjectName("chatScroll")

    stabilize_reference_backgrounds(window)
    app.processEvents()

    assert knowledge.autoFillBackground()
    assert inspector.autoFillBackground()
    assert chat_scroll.autoFillBackground()
    assert chat_scroll.viewport().autoFillBackground()
    assert knowledge.palette().color(QPalette.ColorRole.Window).name().upper() == PALETTE.canvas
    assert inspector.palette().color(QPalette.ColorRole.Window).name().upper() == PALETTE.surface
    assert chat_scroll.viewport().palette().color(QPalette.ColorRole.Window).name().upper() == PALETTE.canvas
