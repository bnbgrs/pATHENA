"""Dense-list scanability and selected-entity identity for pATHENA.

Research, Jobs, Sources and Backup already render compact one-line canonical rows.
This presentation-only pass improves scanning without changing row content: stable
spacing, per-pixel scrolling, right-edge elision, a quiet selected-row treatment and
explicit selected-entity metadata for assistive/status surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer
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

_ACCESSIBILITY_PARITY_TARGETS: tuple[DenseListTarget, ...] = (
    DenseListTarget("persistentKnowledgeList", "Knowledge item"),
    DenseListTarget("persistentClaimList", "Claim"),
    DenseListTarget("semanticReviewList", "contradiction decision"),
    DenseListTarget("claimRelationList", "claim relation"),
    DenseListTarget("researchJobList", "research job"),
    DenseListTarget("researchProposalList", "research proposal"),
    DenseListTarget("durableJobList", "durable job"),
    DenseListTarget("sourceList", "source"),
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
        self._accessibility_labels: dict[QListWidget, str] = {}

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

    def register_accessibility(self, widget: QListWidget, label: str) -> None:
        if widget in self._accessibility_labels:
            return
        self._accessibility_labels[widget] = label
        widget.currentItemChanged.connect(
            lambda _current, _previous, source=widget: self._sync_accessibility(source)
        )
        model = widget.model()
        model.rowsInserted.connect(
            lambda *_args, source=widget: QTimer.singleShot(
                0,
                lambda: self._sync_accessibility(source),
            )
        )
        model.rowsRemoved.connect(
            lambda *_args, source=widget: QTimer.singleShot(
                0,
                lambda: self._sync_accessibility(source),
            )
        )
        model.modelReset.connect(
            lambda source=widget: QTimer.singleShot(
                0,
                lambda: self._sync_accessibility(source),
            )
        )
        widget.setProperty("pathenaDenseListAccessibility", True)
        self._sync_accessibility(widget)

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

    def _sync_accessibility(self, widget: QListWidget) -> None:
        label = self._accessibility_labels[widget]
        for index in range(widget.count()):
            item: QListWidgetItem | None = widget.item(index)
            if item is None:
                continue
            summary = item.text().strip()
            identity = self._identity(item)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, summary)
            description = f"{label.capitalize()} row."
            if identity and identity != summary:
                description += f" Stable identity: {identity}."
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, description)

        count = widget.count()
        current = widget.currentItem()
        identity = self._identity(current)
        noun = label if count == 1 else f"{label}s"
        selection = (
            f" Selected identity: {identity}."
            if current is not None and identity
            else " No row is selected."
        )
        description = f"{count} total {noun} in the list model.{selection}"
        widget.setAccessibleDescription(description)
        widget.setProperty("pathenaDenseListAccessibleScope", description)

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

    parity_count = 0
    for target in _ACCESSIBILITY_PARITY_TARGETS:
        widget = window.findChild(QListWidget, target.object_name)
        if widget is None:
            continue
        controller.register_accessibility(widget, target.label)
        parity_count += 1

    if _DENSE_LIST_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_DENSE_LIST_STYLESHEET}")

    window.setProperty("pathenaDenseListScanabilityController", controller)
    window.setProperty("pathenaDenseListScanabilityManaged", True)
    window.setProperty("pathenaDenseListAccessibilityParityCount", parity_count)
    return tuple(applied)
