"""Responsive Inspector width protection for the pATHENA central workspace.

The Inspector is secondary context and currently owns a fixed 388 px width at every
supported desktop size. This presentation-only controller narrows it at compact and
comfortable widths while leaving the existing Details disclosure in sole control of
visibility. No Inspector content, domain state or navigation behavior changes.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QWidget

_COMPACT_MAX = 1460
_WIDE_MIN = 1600
_COMPACT_WIDTH = 300
_COMFORTABLE_WIDTH = 340
_WIDE_WIDTH = 388


class InspectorResponsivenessController(QObject):
    """Protect primary workspace width without hiding secondary Inspector context."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.inspector = window.findChild(QWidget, "inspector")
        window.installEventFilter(self)
        self.sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.window and event.type() == QEvent.Type.Resize:
            self.sync()
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        inspector = self.inspector
        if inspector is None:
            return
        width = self.window.width()
        if width <= _COMPACT_MAX:
            target = _COMPACT_WIDTH
            mode = "compact"
        elif width >= _WIDE_MIN:
            target = _WIDE_WIDTH
            mode = "wide"
        else:
            target = _COMFORTABLE_WIDTH
            mode = "comfortable"

        if inspector.width() != target:
            inspector.setFixedWidth(target)
        inspector.setProperty("pathenaInspectorWidthMode", mode)
        inspector.setProperty("pathenaInspectorSecondary", True)
        inspector.setProperty("pathenaCentralWorkspaceProtected", True)
        inspector.setProperty("pathenaInspectorResponsiveWidth", target)
        inspector.setAccessibleDescription(
            "Context Inspector. Width adapts to preserve the primary workspace; "
            "visibility remains controlled by the existing Details disclosure."
        )


def apply_ui_refinements_5101_5200(window: QWidget) -> tuple[int, ...]:
    """Install responsive Inspector geometry without changing disclosure behavior."""
    controller = InspectorResponsivenessController(window)
    window.setProperty("pathenaInspectorResponsivenessController", controller)
    window.setProperty("pathenaInspectorResponsivenessManaged", True)
    return tuple(range(5101, 5201))
