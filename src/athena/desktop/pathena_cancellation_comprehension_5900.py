"""Cancellation-phase comprehension for durable Research and Jobs UI.

Cancellation in pATHENA is a durable request/transition, not an instantaneous synonym
for terminal cancellation. This presentation-only controller mirrors the existing
operation and selected-job states into explicit request/requested/terminal metadata.
It never invokes cancellation, changes a job state, or changes button enablement.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QListWidget, QWidget


@dataclass(frozen=True)
class CancellationTarget:
    workspace_name: str
    attribute_name: str
    label: str


_TARGETS: tuple[CancellationTarget, ...] = (
    CancellationTarget("researchWorkspace", "status", "Research status"),
    CancellationTarget("researchWorkspace", "jobs", "Research jobs"),
    CancellationTarget("researchWorkspace", "details", "Research details"),
    CancellationTarget("researchWorkspace", "cancel_button", "Research cancel action"),
    CancellationTarget("researchWorkspace", "query_input", "Research query"),
    CancellationTarget("jobsWorkspace", "status", "Jobs status"),
    CancellationTarget("jobsWorkspace", "jobs", "Durable jobs"),
    CancellationTarget("jobsWorkspace", "details", "Job details"),
    CancellationTarget("jobsWorkspace", "cancel_button", "Job cancel action"),
    CancellationTarget("jobsWorkspace", "scheduler_status", "Scheduler status"),
)

_DIMENSIONS: tuple[str, ...] = (
    "cancellation phase",
    "request versus terminal distinction",
    "selected cancellation state",
    "assistive cancellation explanation",
    "tooltip cancellation explanation",
    "cancellation ownership metadata",
    "pending-request metadata",
    "terminal-cancellation metadata",
    "cancellation status guidance",
    "cancellation synchronization",
)

UI_REFINEMENT_TASKS_5801_5900: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class CancellationComprehensionController(QObject):
    """Expose truthful cancellation phases from existing workspace state."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._targets: list[tuple[QWidget, QWidget, CancellationTarget]] = []
        self._last: dict[QWidget, tuple[str, str]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(
        self,
        workspace: QWidget,
        widget: QWidget,
        target: CancellationTarget,
    ) -> None:
        self._targets.append((workspace, widget, target))
        self._sync_one(workspace, widget, target)

    def sync(self) -> None:
        for workspace, widget, target in self._targets:
            self._sync_one(workspace, widget, target)

    def _sync_one(
        self,
        workspace: QWidget,
        widget: QWidget,
        target: CancellationTarget,
    ) -> None:
        state = self._selected_state(workspace)
        phase = self._phase(workspace, state)
        signature = (phase, state)
        if self._last.get(widget) == signature:
            return
        self._last[widget] = signature

        explanation = self._explanation(phase, state)
        widget.setProperty("pathenaCancellationPhase", phase)
        widget.setProperty("pathenaCancellationSelectedState", state)
        widget.setProperty("pathenaCancellationRequestPending", phase in {"requesting", "requested"})
        widget.setProperty("pathenaCancellationTerminal", phase == "cancelled")
        widget.setProperty("pathenaCancellationObservedOnly", True)
        widget.setProperty("pathenaCancellationSynchronized", True)

        widget.setAccessibleDescription(
            self._with_suffix(
                widget.accessibleDescription(),
                " Cancellation: ",
                explanation,
            )
        )
        widget.setToolTip(
            self._with_suffix(widget.toolTip(), "\nCancellation: ", explanation)
        )
        widget.setStatusTip(f"Cancellation: {explanation}")

    @staticmethod
    def _phase(workspace: QWidget, state: str) -> str:
        operation = str(getattr(workspace, "_operation", "") or "")
        if operation == "cancel":
            return "requesting"
        if state == "cancel_requested":
            return "requested"
        if state == "cancelled":
            return "cancelled"
        if state in {"completed", "failed"}:
            return "terminal-other"
        if state:
            return "requestable"
        return "no-selection"

    @staticmethod
    def _selected_state(workspace: QWidget) -> str:
        value = getattr(workspace, "_selected_state", None)
        if isinstance(value, str) and value:
            return value.casefold()

        listing = getattr(workspace, "jobs", None)
        if isinstance(listing, QListWidget):
            item = listing.currentItem()
            if item is not None:
                text = item.text().strip()
                if text:
                    return text.split(maxsplit=1)[0].casefold()
        return ""

    @staticmethod
    def _explanation(phase: str, state: str) -> str:
        if phase == "requesting":
            return "A cancellation request is being persisted; the job is not yet terminally cancelled."
        if phase == "requested":
            return "Cancellation has been requested and persisted; terminal cancellation is still pending."
        if phase == "cancelled":
            return "The selected job is terminally cancelled."
        if phase == "terminal-other":
            return f"The selected job is already terminal with state {state}; cancellation is not pending."
        if phase == "requestable":
            return f"The selected job is {state}; cancellation would create a durable request first."
        return "No job is selected, so there is no cancellation context."

    @staticmethod
    def _with_suffix(current: str, marker: str, suffix: str) -> str:
        base = current.split(marker, 1)[0].rstrip()
        if not base:
            return f"Cancellation: {suffix}"
        return f"{base}{marker}{suffix}"


def _resolve(window: QWidget, target: CancellationTarget) -> tuple[QWidget, QWidget] | None:
    workspace = window.findChild(QWidget, target.workspace_name)
    if workspace is None:
        return None
    widget = getattr(workspace, target.attribute_name, None)
    if isinstance(widget, QWidget):
        return workspace, widget
    return None


def apply_ui_refinements_5801_5900(window: QWidget) -> tuple[int, ...]:
    """Install cancellation-phase comprehension on existing durable-work surfaces."""
    controller = CancellationComprehensionController(window)
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        resolved = _resolve(window, target)
        if resolved is None:
            continue
        workspace, widget = resolved
        controller.register(workspace, widget, target)
        start = 5801 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaCancellationComprehensionController", controller)
    window.setProperty("pathenaCancellationComprehensionManaged", True)
    return tuple(applied)
