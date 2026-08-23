"""Dense-list scanability and selected-entity identity for pATHENA.

Research, Jobs, Sources and Backup already render compact one-line canonical rows.
This presentation-only pass improves scanning without changing row content: stable
spacing, per-pixel scrolling, right-edge elision, a quiet selected-row treatment and
explicit selected-entity metadata for assistive/status surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QWidget


@dataclass(frozen=True)
class DenseListTarget:
    object_name: str
    label: str


_TARGETS: tuple[DenseListTarget, ...] = (
    DenseListTarget("researchJobList", "research job"),
    DenseListTarget("durableJobList", "durable job"),
    DenseListTarget("sourceList", "source"),
    DenseListTarget("backupSnapshotList", "backup snapshot"),
)

_DENSE_LIST_STYLESHEET = """
/* pATHENA dense list scanability */
QListWidget[pathenaDenseList="true"]::item {
    padding: 5px 7px;
    border-left: 2px solid transparent;
}
QListWidget[pathenaDenseList="true"]::item:selected {
    background: #101010;
    border-left: 2px solid #F26A21;
}
"""


class DenseListScanabilityController(QObject):
    """Keep selected-row identity explicit while preserving canonical row text."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._labels: dict[QListWidget, str] = {}

    def register(self, widget: QListWidget, label: str) -> None:
        self._labels[widget] = label
        widget.setProperty("pathenaDenseList", True)
        widget.setProperty("pathenaDenseListLabel", label)
        widget.setSpacing(1)
        widget.setUniformItemSizes(True)
        widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        widget.currentItemChanged.connect(
            lambda current, _previous, source=widget: self._selection_changed(
                source,
                current,
            )
        )
        self._selection_changed(widget, widget.currentItem())

    def _selection_changed(
        self,
        widget: QListWidget,
        current: QListWidgetItem | None,
    ) -> None:
        label = self._labels[widget]
        identity = self._identity(current)
        summary = "" if current is None else current.text().strip()
        widget.setProperty("pathenaSelectedEntityIdentity", identity)
        widget.setProperty("pathenaSelectedEntitySummary", summary[:240])
        widget.setProperty("pathenaSelectedEntityPresent", current is not None)
        if current is None:
            widget.setStatusTip(f"No {label} selected.")
            widget.setAccessibleDescription(
                f"{label.capitalize()} list. No row is selected."
            )
            return
        widget.setStatusTip(f"Selected {label}: {summary}")
        widget.setAccessibleDescription(
            f"{label.capitalize()} list. Selected row: {summary}."
        )

    @staticmethod
    def _identity(item: QListWidgetItem | None) -> str:
        if item is None:
            return ""
        value = item.data(Qt.ItemDataRole.UserRole)
        return str(value) if value is not None else item.text()


def apply_ui_refinements_4801_4900(window: QWidget) -> tuple[int, ...]:
    """Install scanability and selection-identity behavior on dense canonical lists."""
    controller = DenseListScanabilityController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QListWidget, target.object_name)
        if widget is None:
            continue
        controller.register(widget, target.label)
        start = 4801 + index * 20
        applied.extend(range(start, start + 20))

    if _DENSE_LIST_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_DENSE_LIST_STYLESHEET}")

    window.setProperty("pathenaDenseListScanabilityController", controller)
    window.setProperty("pathenaDenseListScanabilityManaged", True)
    return tuple(applied)
