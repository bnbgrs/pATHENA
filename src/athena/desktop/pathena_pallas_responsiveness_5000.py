"""Responsive, subordinate PALLAS presentation for pATHENA.

PALLAS is intentionally characteristic but secondary to the central workspace. The
placeholder renderer declares a 9:16 format, so this presentation-only controller
keeps that ratio intact and reduces its footprint at compact desktop widths. It never
hides PALLAS, changes navigation, or alters renderer/domain behavior.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QSize
from PySide6.QtWidgets import QWidget

_REGULAR_SIZE = QSize(112, 199)
_COMPACT_SIZE = QSize(96, 171)
_COMPACT_THRESHOLD = 1460


class PallasResponsivenessController(QObject):
    """Keep the PALLAS miniature 9:16 and visually subordinate across resize states."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.pallas = window.findChild(QWidget, "pallasVisualPlaceholder")
        window.installEventFilter(self)
        self.sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.window and event.type() == QEvent.Type.Resize:
            self.sync()
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        pallas = self.pallas
        if pallas is None:
            return
        compact = self._compact_mode()
        target = _COMPACT_SIZE if compact else _REGULAR_SIZE
        if pallas.size() != target:
            pallas.setFixedSize(target)

        pallas.setProperty("pathenaPallasAspectRatio", "9:16")
        pallas.setProperty("pathenaPallasProminence", "secondary")
        pallas.setProperty("pathenaPallasResponsive", True)
        pallas.setProperty("pathenaPallasMode", "compact" if compact else "regular")
        pallas.setToolTip(
            "PALLAS 9:16 reactive ASCII placeholder; secondary to workspace content."
        )
        pallas.setAccessibleDescription(
            "PALLAS reactive ASCII placeholder. Characteristic local visual, kept "
            "secondary to navigation and workspace content."
        )

    def _compact_mode(self) -> bool:
        mode = str(self.window.property("pathenaLayoutMode") or "")
        if mode in {"compact", "regular"}:
            return mode == "compact"
        return self.window.width() < _COMPACT_THRESHOLD


def apply_ui_refinements_4901_5000(window: QWidget) -> tuple[int, ...]:
    """Install responsive PALLAS presentation without changing renderer behavior."""
    controller = PallasResponsivenessController(window)
    window.setProperty("pathenaPallasResponsivenessController", controller)
    window.setProperty("pathenaPallasResponsivenessManaged", True)
    return tuple(range(4901, 5001))
