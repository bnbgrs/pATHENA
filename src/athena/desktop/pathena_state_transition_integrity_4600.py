"""Selection-scoped UI state transition integrity for pATHENA.

The semantic error-coverage layer can legitimately mark detail surfaces as error or
success after an operation. When the user selects a different entity, that old
coverage-owned result must not visually follow the new selection. This UI-only pass
binds detail state to selection identity and clears only coverage-owned terminal state
on a real selection change. Busy state and externally owned UI state are preserved.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget


@dataclass(frozen=True)
class TransitionBinding:
    selection_object_name: str
    detail_object_name: str
    label: str


_BINDINGS: tuple[TransitionBinding, ...] = (
    TransitionBinding(
        "persistentKnowledgeList",
        "persistentKnowledgeDetails",
        "canonical knowledge",
    ),
    TransitionBinding(
        "persistentClaimList",
        "persistentClaimDetails",
        "canonical claim",
    ),
    TransitionBinding(
        "semanticReviewList",
        "semanticReviewDetails",
        "contradiction decision",
    ),
    TransitionBinding("researchJobList", "researchDetails", "research job"),
    TransitionBinding("durableJobList", "jobDetails", "durable job"),
    TransitionBinding("sourceList", "sourceDetails", "source"),
    TransitionBinding("backupSnapshotList", "backupDetails", "backup snapshot"),
)


class StateTransitionIntegrityController(QObject):
    """Keep selection-scoped terminal presentation state attached to its entity."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._details: dict[QListWidget, QWidget] = {}
        self._identity: dict[QListWidget, object | None] = {}

    def register(self, selection: QListWidget, detail: QWidget, label: str) -> None:
        self._details[selection] = detail
        self._identity[selection] = self._current_identity(selection.currentItem())
        selection.currentItemChanged.connect(
            lambda current, previous, source=selection: self._selection_changed(
                source,
                current,
                previous,
            )
        )
        detail.setProperty("pathenaSelectionScopedState", True)
        detail.setProperty("pathenaSelectionScopeLabel", label)
        detail.setProperty(
            "pathenaSelectionScopeIdentity",
            self._identity_text(self._identity[selection]),
        )

    def _selection_changed(
        self,
        selection: QListWidget,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        old_identity = self._identity.get(selection)
        new_identity = self._current_identity(current)
        self._identity[selection] = new_identity

        detail = self._details[selection]
        detail.setProperty(
            "pathenaSelectionScopeIdentity",
            self._identity_text(new_identity),
        )
        if old_identity == new_identity:
            return

        detail.setProperty("pathenaSelectionChanged", True)
        detail.setProperty(
            "pathenaPreviousSelectionScopeIdentity",
            self._identity_text(old_identity),
        )
        self._clear_stale_owned_terminal_state(detail)

    @staticmethod
    def _clear_stale_owned_terminal_state(detail: QWidget) -> None:
        if bool(detail.property("pathenaLongRunningWork")):
            detail.setProperty("pathenaSelectionStateResetDeferred", True)
            return

        ui_state = str(detail.property("pathenaUiState") or "idle")
        owned_state = str(detail.property("pathenaCoverageOwnedState") or "")
        if owned_state not in {"error", "success"} or ui_state != owned_state:
            return

        detail.setProperty("pathenaUiState", "idle")
        detail.setProperty("pathenaCoverageOwnedState", "")
        detail.setProperty("pathenaSelectionStateReset", True)
        detail.setProperty("pathenaErrorCoverageClassification", "neutral")

    @staticmethod
    def _current_identity(item: QListWidgetItem | None) -> object | None:
        if item is None:
            return None
        identity = item.data(Qt.ItemDataRole.UserRole)
        if identity is not None:
            return identity
        return item.text()

    @staticmethod
    def _identity_text(identity: object | None) -> str:
        return "" if identity is None else str(identity)


def apply_ui_refinements_4501_4600(window: QWidget) -> tuple[int, ...]:
    """Install selection-scoped state integrity on existing detail/list pairs."""
    controller = StateTransitionIntegrityController(window)
    applied: list[int] = []

    for index, binding in enumerate(_BINDINGS):
        selection = window.findChild(QListWidget, binding.selection_object_name)
        detail = window.findChild(QWidget, binding.detail_object_name)
        if selection is None or detail is None:
            continue
        controller.register(selection, detail, binding.label)
        start = 4501 + index * 10
        applied.extend(range(start, start + 10))

    window.setProperty("pathenaStateTransitionIntegrityController", controller)
    window.setProperty("pathenaStateTransitionBindingCount", len(applied) // 10)
    window.setProperty("pathenaStateTransitionTaskCount", len(applied))
    return tuple(applied)
