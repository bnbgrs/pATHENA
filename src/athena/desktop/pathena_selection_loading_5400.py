"""Selection-to-detail loading affordance for pATHENA list/detail workspaces.

Existing workspaces already set detail panes to semantic busy/success/error states while
loading the selected entity. This presentation-only controller mirrors that state back
to the owning list so the selected row remains the clear identity anchor. It never
starts work, changes selection or modifies detail state.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtWidgets import QListWidget, QWidget


@dataclass(frozen=True)
class SelectionLoadingPair:
    list_name: str
    detail_name: str
    label: str


_PAIRS: tuple[SelectionLoadingPair, ...] = (
    SelectionLoadingPair(
        "persistentKnowledgeList",
        "persistentKnowledgeDetails",
        "Knowledge",
    ),
    SelectionLoadingPair("persistentClaimList", "persistentClaimDetails", "Claim"),
    SelectionLoadingPair(
        "semanticReviewList",
        "semanticReviewDetails",
        "decision",
    ),
    SelectionLoadingPair("researchJobList", "researchDetails", "research job"),
    SelectionLoadingPair("durableJobList", "jobDetails", "durable job"),
    SelectionLoadingPair("sourceList", "sourceDetails", "Source"),
    SelectionLoadingPair("backupSnapshotList", "backupDetails", "backup snapshot"),
)

_SELECTION_STYLESHEET = """
/* pATHENA selection-to-detail loading */
QListWidget[pathenaDetailLoading="true"]::item:selected {
    border-right: 1px solid #555555;
}
"""


class SelectionLoadingController(QObject):
    """Mirror selected detail state onto its owning list without changing behavior."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._pairs: list[tuple[QListWidget, QWidget, str]] = []
        self._last: dict[QListWidget, tuple[str, str]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, listing: QListWidget, detail: QWidget, label: str) -> None:
        self._pairs.append((listing, detail, label))
        listing.setProperty("pathenaDetailOwnerList", True)
        detail.setProperty("pathenaSelectionOwnedDetail", True)
        self._sync_one(listing, detail, label)

    def sync(self) -> None:
        for listing, detail, label in self._pairs:
            self._sync_one(listing, detail, label)

    def _sync_one(self, listing: QListWidget, detail: QWidget, label: str) -> None:
        state = str(detail.property("pathenaUiState") or "idle")
        identity = self._identity(listing)
        signature = (state, identity)
        if self._last.get(listing) == signature:
            return
        self._last[listing] = signature

        has_selection = bool(identity)
        loading = has_selection and state == "busy"
        listing.setProperty("pathenaDetailLoading", loading)
        listing.setProperty("pathenaSelectedDetailState", state)
        listing.setProperty("pathenaSelectedDetailIdentity", identity)
        listing.setProperty("pathenaSelectionAnchored", has_selection)

        if not has_selection:
            listing.setStatusTip(f"Select a {label} to inspect its details.")
        elif loading:
            listing.setStatusTip(f"Selected {label} remains active while details load.")
        elif state == "error":
            listing.setStatusTip(f"Selected {label} remains active; detail loading failed.")
        else:
            listing.setStatusTip(f"Selected {label} is the active detail context.")

        style = listing.style()
        style.unpolish(listing)
        style.polish(listing)
        listing.update()

    @staticmethod
    def _identity(listing: QListWidget) -> str:
        item = listing.currentItem()
        if item is None:
            return ""
        identity = item.data(Qt.ItemDataRole.UserRole)
        return str(identity) if identity is not None else item.text()


def apply_ui_refinements_5301_5400(window: QWidget) -> tuple[int, ...]:
    """Install selection-to-detail state mirroring on existing list/detail pairs."""
    controller = SelectionLoadingController(window)
    applied: list[int] = []

    for index, pair in enumerate(_PAIRS):
        listing = window.findChild(QListWidget, pair.list_name)
        detail = window.findChild(QWidget, pair.detail_name)
        if listing is None or detail is None:
            continue
        controller.register(listing, detail, pair.label)
        start = 5301 + index * 14
        applied.extend(range(start, min(start + 14, 5401)))

    if _SELECTION_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_SELECTION_STYLESHEET}")

    window.setProperty("pathenaSelectionLoadingController", controller)
    window.setProperty("pathenaSelectionLoadingManaged", True)
    return tuple(applied)
