"""Deterministic painted backgrounds for the eleven-screen reference shell.

Qt style sheets do not always make plain ``QWidget`` workspace roots paint an
opaque background. The legacy desktop palette can therefore leak through as
near-black ``#060606`` blocks even when the final QSS correctly asks for the
reference navy. This module fixes only that paint contract; it does not own
workspace state or interaction.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QAbstractScrollArea, QWidget

from athena.desktop.pathena_design_tokens import PALETTE

_CANVAS_ROOTS = (
    "pageChat",
    "pageKnowledge",
    "pageResearch",
    "pageJobs",
    "pageFiles",
    "pageSystem",
    "pageSettings",
    "knowledgeWorkspace",
    "researchWorkspace",
    "jobsWorkspace",
    "filesWorkspace",
    "systemWorkspace",
    "conversation",
    "pallasShellWorkspaceHost",
    "pallasShellWorkspace",
    "pallasWorkspace",
)

_SURFACE_ROOTS = (
    "inspector",
    "inspectorPanel",
    "inspectorScrollContent",
    "helpSecondaryNavigation",
    "comfyUiIntegrationNav",
    "comfyUiConnectionPanel",
)

_CANVAS_SCROLL_AREAS = (
    "chatScroll",
    "knowledgeWorkspaceScroll",
)

_SURFACE_SCROLL_AREAS = ("inspectorScroll",)


def _paint(widget: QWidget, color: str) -> None:
    """Give a Qt widget an explicit Window/Base palette and styled background."""
    qcolor = QColor(color)
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, qcolor)
    palette.setColor(QPalette.ColorRole.Base, qcolor)
    widget.setPalette(palette)
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    widget.update()


def _paint_named(window: QWidget, object_name: str, color: str) -> QWidget | None:
    widget = window.findChild(QWidget, object_name)
    if widget is None:
        return None
    _paint(widget, color)
    return widget


def _paint_scroll_area(area: QAbstractScrollArea, color: str) -> None:
    _paint(area, color)
    _paint(area.viewport(), color)


def stabilize_reference_backgrounds(window: QWidget) -> None:
    """Prevent legacy near-black palette colours from leaking through workspaces."""
    _paint(window, PALETTE.canvas)

    for object_name in _CANVAS_ROOTS:
        _paint_named(window, object_name, PALETTE.canvas)

    for object_name in _SURFACE_ROOTS:
        _paint_named(window, object_name, PALETTE.surface)

    for object_name in _CANVAS_SCROLL_AREAS:
        area = window.findChild(QAbstractScrollArea, object_name)
        if area is not None:
            _paint_scroll_area(area, PALETTE.canvas)

    for object_name in _SURFACE_SCROLL_AREAS:
        area = window.findChild(QAbstractScrollArea, object_name)
        if area is not None:
            _paint_scroll_area(area, PALETTE.surface)
