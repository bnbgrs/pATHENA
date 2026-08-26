"""Visible provenance for retained list/detail content during asynchronous loading.

List/detail workspaces may intentionally leave the previous detail text visible while
a newly selected entity loads. This presentation-only controller inserts one quiet
metadata line before each existing detail pane and distinguishes current content from
retained content without clearing, editing or fabricating detail data.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QBoxLayout, QLabel, QListWidget, QListWidgetItem, QPlainTextEdit, QWidget


@dataclass(frozen=True)
class DetailProvenancePair:
    list_name: str
    detail_name: str
    label: str


_PAIRS: tuple[DetailProvenancePair, ...] = (
    DetailProvenancePair(
        "persistentKnowledgeList",
        "persistentKnowledgeDetails",
        "Knowledge",
    ),
    DetailProvenancePair("persistentClaimList", "persistentClaimDetails", "Claim"),
    DetailProvenancePair("semanticReviewList", "semanticReviewDetails", "Decision"),
    DetailProvenancePair("researchJobList", "researchDetails", "Research job"),
    DetailProvenancePair("durableJobList", "jobDetails", "Durable job"),
    DetailProvenancePair("sourceList", "sourceDetails", "Source"),
    DetailProvenancePair("backupSnapshotList", "backupDetails", "Backup snapshot"),
)

_DETAIL_PROVENANCE_STYLESHEET = """
/* pATHENA retained-detail provenance */
QLabel#pathenaDetailProvenance {
    color: #6F6F6F;
    font-size: 9px;
    padding: 1px 2px 3px 2px;
}
QLabel#pathenaDetailProvenance[pathenaDetailProvenanceMode="retained"],
QLabel#pathenaDetailProvenance[pathenaDetailProvenanceMode="retained-error"] {
    color: #9A8876;
}
"""


class DetailProvenanceController(QObject):
    """Track which selected identity the currently visible detail text belongs to."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._pairs: dict[QWidget, tuple[QListWidget, QLabel, str]] = {}
        self._rendered_identity: dict[QWidget, str] = {}
        self._last_signature: dict[QWidget, tuple[str, str, str, bool]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, listing: QListWidget, detail: QWidget, label: str) -> None:
        provenance = self._insert_provenance_label(detail)
        if provenance is None:
            return
        self._pairs[detail] = (listing, provenance, label)
        listing.currentItemChanged.connect(self._schedule_sync)

        selected = self._identity(listing)
        state = str(detail.property("pathenaUiState") or "idle")
        if selected and state != "busy" and self._has_content(detail):
            self._rendered_identity[detail] = selected

        detail.setProperty("pathenaDetailProvenanceManaged", True)
        provenance.setProperty("pathenaDetailProvenanceManaged", True)
        self._sync_one(detail)

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        for detail in self._pairs:
            self._sync_one(detail)

    def _sync_one(self, detail: QWidget) -> None:
        listing, provenance, label = self._pairs[detail]
        selected = self._identity(listing)
        state = str(detail.property("pathenaUiState") or "idle")
        rendered = self._rendered_identity.get(detail, "")
        has_content = self._has_content(detail)
        signature = (selected, state, rendered, has_content)
        if self._last_signature.get(detail) == signature:
            return
        self._last_signature[detail] = signature

        mode, text, next_rendered = self._presentation(
            label=label,
            selected=selected,
            rendered=rendered,
            state=state,
            has_content=has_content,
        )
        if next_rendered != rendered:
            self._rendered_identity[detail] = next_rendered

        provenance.setText(text)
        provenance.setVisible(bool(text))
        provenance.setProperty("pathenaDetailProvenanceMode", mode)
        provenance.setAccessibleName(f"{label} detail provenance")
        provenance.setAccessibleDescription(text)
        detail.setProperty("pathenaDetailContentIdentity", next_rendered)
        detail.setProperty("pathenaDetailSelectedIdentity", selected)
        detail.setProperty("pathenaDetailProvenanceMode", mode)
        listing.setProperty("pathenaDetailProvenanceMode", mode)

        style = provenance.style()
        style.unpolish(provenance)
        style.polish(provenance)
        provenance.update()

    @staticmethod
    def _presentation(
        *,
        label: str,
        selected: str,
        rendered: str,
        state: str,
        has_content: bool,
    ) -> tuple[str, str, str]:
        selected_short = _short_identity(selected)
        rendered_short = _short_identity(rendered)

        if not selected:
            return "empty", "", ""

        if state == "busy":
            if has_content and rendered and rendered != selected:
                text = (
                    f"RETAINED · {rendered_short} · loading {selected_short}"
                )
                return "retained", text, rendered
            return "loading", f"LOADING · {selected_short}", rendered

        if state == "error":
            if has_content and rendered and rendered != selected:
                text = (
                    f"RETAINED · {rendered_short} · load failed for {selected_short}"
                )
                return "retained-error", text, rendered
            return "error", f"LOAD ERROR · {selected_short}", rendered

        if state == "success":
            return "current", f"CURRENT · {selected_short}", selected

        if has_content:
            if not rendered:
                return "current", f"CURRENT · {selected_short}", selected
            if rendered == selected:
                return "current", f"CURRENT · {selected_short}", rendered
            text = f"RETAINED · {rendered_short} · selected {selected_short}"
            return "retained", text, rendered

        return "empty", f"SELECTED · {selected_short} · no detail loaded", ""

    @staticmethod
    def _insert_provenance_label(detail: QWidget) -> QLabel | None:
        parent = detail.parentWidget()
        if parent is None:
            return None
        layout = parent.layout()
        if not isinstance(layout, QBoxLayout):
            return None
        index = layout.indexOf(detail)
        if index < 0:
            return None

        provenance = QLabel(parent)
        provenance.setObjectName("pathenaDetailProvenance")
        provenance.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        provenance.setVisible(False)
        layout.insertWidget(index, provenance)
        return provenance

    @staticmethod
    def _identity(listing: QListWidget) -> str:
        item: QListWidgetItem | None = listing.currentItem()
        if item is None:
            return ""
        value = item.data(Qt.ItemDataRole.UserRole)
        if value is None:
            value = item.text()
        return " ".join(str(value).split())

    @staticmethod
    def _has_content(detail: QWidget) -> bool:
        if isinstance(detail, QPlainTextEdit):
            return bool(detail.toPlainText().strip())
        if isinstance(detail, QLabel):
            return bool(detail.text().strip())
        return False


def _short_identity(identity: str) -> str:
    normalized = " ".join(identity.split())
    if len(normalized) <= 24:
        return normalized
    return f"{normalized[:21]}…"


def apply_detail_provenance(window: QWidget) -> DetailProvenanceController:
    """Install visible detail provenance on existing asynchronous list/detail pairs."""
    controller = DetailProvenanceController(window)
    for pair in _PAIRS:
        listing = window.findChild(QListWidget, pair.list_name)
        detail = window.findChild(QWidget, pair.detail_name)
        if listing is None or detail is None:
            continue
        controller.register(listing, detail, pair.label)

    if _DETAIL_PROVENANCE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_DETAIL_PROVENANCE_STYLESHEET}")

    window.setProperty("pathenaDetailProvenanceController", controller)
    window.setProperty("pathenaDetailProvenanceManaged", True)
    return controller
