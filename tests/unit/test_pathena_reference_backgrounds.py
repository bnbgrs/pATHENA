from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QFrame, QScrollArea, QWidget

from athena.desktop.pathena_design_tokens import PALETTE
from athena.desktop.pathena_reference_backgrounds import stabilize_reference_backgrounds


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _window_color(widget: QWidget) -> str:
    return widget.palette().color(QPalette.ColorRole.Window).name().upper()


def test_reference_backgrounds_paint_workspace_inspector_and_scroll_viewports() -> None:
    app = _app()
    window = QWidget()
    knowledge = QWidget(window)
    knowledge.setObjectName("knowledgeWorkspace")
    inspector = QFrame(window)
    inspector.setObjectName("inspector")
    inspector_scroll = QScrollArea(window)
    inspector_scroll.setObjectName("inspectorScroll")
    inspector_content = QWidget()
    inspector_content.setObjectName("inspectorScrollContent")
    inspector_scroll.setWidget(inspector_content)
    chat_scroll = QScrollArea(window)
    chat_scroll.setObjectName("chatScroll")

    stabilize_reference_backgrounds(window)
    app.processEvents()

    assert knowledge.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
    assert inspector.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
    assert inspector_scroll.viewport().testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
    assert _window_color(knowledge) == PALETTE.canvas
    assert _window_color(inspector) == PALETTE.surface
    assert _window_color(inspector_scroll.viewport()) == PALETTE.surface
    assert _window_color(inspector_content) == PALETTE.surface
    assert _window_color(chat_scroll.viewport()) == PALETTE.canvas
