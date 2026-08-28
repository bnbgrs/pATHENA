"""Read-only versus mutating interaction-boundary clarity for pATHENA.

The desktop deliberately places inspection and action surfaces close together. This
presentation-only pass labels that boundary using existing widgets, action roles and
decision consequences. It does not add controls, change enabled state, invoke domain
commands or reinterpret a read-only pane as an editor.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject
from PySide6.QtWidgets import QAbstractButton, QPlainTextEdit, QWidget


@dataclass(frozen=True)
class BoundaryTarget:
    workspace_name: str | None
    attribute_name: str | None
    object_name: str | None
    label: str
    boundary: str
    explanation: str


_TARGETS: tuple[BoundaryTarget, ...] = (
    BoundaryTarget(None, None, "inspectorBody", "Inspector provenance", "read-only", "Inspects current provenance; it does not mutate canonical data."),
    BoundaryTarget("knowledgeWorkspace", "knowledge_details", None, "Knowledge details", "read-only", "Inspects the selected canonical Knowledge item and provenance."),
    BoundaryTarget("knowledgeWorkspace", "claim_details", None, "Claim details", "read-only", "Inspects the selected canonical Claim and evidence."),
    BoundaryTarget("knowledgeWorkspace", "review_details", None, "Contradiction details", "read-only", "Inspects both sides of the pending decision; decision buttons remain separate."),
    BoundaryTarget("researchWorkspace", "details", None, "Research details", "read-only", "Inspects the selected durable research run and its current state."),
    BoundaryTarget("jobsWorkspace", "details", None, "Job details", "read-only", "Inspects checkpoints, leases and pinned durable-job state."),
    BoundaryTarget("filesWorkspace", "details", None, "Source details", "read-only", "Inspects capture and retrieval-processing state for the selected Source."),
    BoundaryTarget("systemWorkspace", "detail", None, "System runtime", "read-only", "Reports current local runtime status without changing it."),
    BoundaryTarget("backupWorkspace", "details", None, "Backup details", "read-only", "Displays backup operation output and selected snapshot details."),
    BoundaryTarget("knowledgeWorkspace", "history_button", None, "Knowledge history", "inspection-action", "Loads immutable Knowledge revision history for inspection."),
    BoundaryTarget("knowledgeWorkspace", "claim_history_button", None, "Claim history", "inspection-action", "Loads immutable Claim revision history for inspection."),
    BoundaryTarget("knowledgeWorkspace", "review_accept_button", None, "Accept contradiction", "mutation", "Commits the selected reviewed contradiction decision through the existing knowledge command."),
    BoundaryTarget("knowledgeWorkspace", "review_reject_button", None, "Reject contradiction", "mutation", "Rejects the selected pending contradiction decision through the existing knowledge command."),
    BoundaryTarget("knowledgeWorkspace", None, "knowledgeAcceptanceButton", "Add reviewed items", "mutation", "Commits only the already reviewed canonical preflight after revalidation."),
    BoundaryTarget("researchWorkspace", "cancel_button", None, "Cancel research", "mutation", "Persists a cancellation request for the selected durable research run."),
    BoundaryTarget("jobsWorkspace", "pause_button", None, "Pause job", "mutation", "Requests the existing durable-job pause transition for the selected eligible job."),
    BoundaryTarget("jobsWorkspace", "resume_button", None, "Resume job", "mutation", "Requests the existing durable-job resume transition for the selected paused job."),
    BoundaryTarget("jobsWorkspace", "cancel_button", None, "Cancel job", "mutation", "Persists cancellation for the selected non-terminal durable job."),
    BoundaryTarget("filesWorkspace", "process_button", None, "Process Source", "mutation", "Queues representation and chunking or retry for the selected eligible Source."),
    BoundaryTarget("backupWorkspace", "restore_button", None, "Restore isolated", "mutation-isolated", "Restores the selected snapshot only into a new isolated root; the live runtime is not overwritten."),
)

_DIMENSIONS: tuple[str, ...] = (
    "interaction boundary role",
    "read-only or mutation explanation",
    "assistive boundary description",
    "tooltip boundary guidance",
    "boundary diagnostic metadata",
)

UI_REFINEMENT_TASKS_5701_5800: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_BOUNDARY_STYLESHEET = """
/* pATHENA interaction-boundary clarity */
QPlainTextEdit[pathenaInteractionBoundary="read-only"] {
    background: #080808;
}
QPushButton[pathenaInteractionBoundary="inspection-action"] {
    border-color: #2A2A2A;
}
"""


class MutationBoundaryController(QObject):
    """Keep interaction-boundary guidance attached to existing surfaces."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._targets: dict[QWidget, BoundaryTarget] = {}

    def register(self, widget: QWidget, target: BoundaryTarget) -> None:
        self._targets[widget] = target
        widget.installEventFilter(self)
        self._sync(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            isinstance(watched, QWidget)
            and watched in self._targets
            and (
                event.type() == QEvent.Type.EnabledChange
                or isinstance(event, QDynamicPropertyChangeEvent)
                and bytes(event.propertyName().data()) == b"pathenaUiState"
            )
        ):
            self._sync(watched)
        return super().eventFilter(watched, event)

    def _sync(self, widget: QWidget) -> None:
        target = self._targets[widget]
        widget.setProperty("pathenaInteractionBoundary", target.boundary)
        widget.setProperty("pathenaBoundaryExplanation", target.explanation)
        widget.setProperty("pathenaMutationCapable", target.boundary.startswith("mutation"))
        widget.setProperty("pathenaReadOnlyInspection", target.boundary == "read-only")
        widget.setProperty("pathenaBoundarySynchronized", True)

        detail = f"Interaction boundary: {target.explanation}"
        widget.setAccessibleDescription(
            self._with_suffix(widget.accessibleDescription(), " Interaction boundary: ", target.explanation)
        )
        widget.setToolTip(
            self._with_suffix(widget.toolTip(), "\nInteraction boundary: ", target.explanation)
        )
        widget.setStatusTip(detail)

        if isinstance(widget, QPlainTextEdit):
            widget.setProperty("pathenaVerifiedReadOnly", widget.isReadOnly())
        if isinstance(widget, QAbstractButton):
            widget.setProperty("pathenaBoundaryActionRole", widget.property("pathenaActionRole") or "")

        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()

    @staticmethod
    def _with_suffix(current: str, marker: str, suffix: str) -> str:
        boundary_label = "Interaction boundary:"
        boundary_index = current.find(boundary_label)
        base = (
            current[:boundary_index].rstrip()
            if boundary_index >= 0
            else current.rstrip()
        )
        if not base:
            return f"{boundary_label} {suffix}"
        return f"{base}{marker}{suffix}"


def _resolve(window: QWidget, target: BoundaryTarget) -> QWidget | None:
    workspace = window
    if target.workspace_name is not None:
        found = window.findChild(QWidget, target.workspace_name)
        if found is None:
            return None
        workspace = found
    if target.attribute_name is not None:
        candidate = getattr(workspace, target.attribute_name, None)
        return candidate if isinstance(candidate, QWidget) else None
    if target.object_name is not None:
        return workspace.findChild(QWidget, target.object_name)
    return None


def apply_ui_refinements_5701_5800(window: QWidget) -> tuple[int, ...]:
    """Install explicit interaction-boundary guidance on existing UI surfaces."""
    controller = MutationBoundaryController(window)
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = _resolve(window, target)
        if widget is None:
            continue
        controller.register(widget, target)
        start = 5701 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    if _BOUNDARY_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_BOUNDARY_STYLESHEET}")
    window.setProperty("pathenaMutationBoundaryController", controller)
    window.setProperty("pathenaMutationBoundaryManaged", True)
    return tuple(applied)
