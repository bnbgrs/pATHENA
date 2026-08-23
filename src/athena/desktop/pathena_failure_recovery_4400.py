"""Failure comprehension and recovery refinements 4301-4400 for pATHENA.

This presentation-only pass builds on the existing semantic ``error`` UI state. It
explains what failed, what remains preserved, where the existing failure evidence is
visible and which already-wired action can safely refresh or retry the view. It does
not add retry behavior, mutate domain state, or reinterpret backend failures.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject
from PySide6.QtWidgets import QAbstractButton, QWidget


@dataclass(frozen=True)
class FailureTarget:
    object_name: str
    label: str
    failure: str
    preserved: str
    recovery: str
    evidence: str
    recovery_workspace: str | None = None
    recovery_attribute: str | None = None


_TARGETS: tuple[FailureTarget, ...] = (
    FailureTarget(
        "knowledgeReviewState",
        "knowledge review state",
        "The latest Knowledge review operation did not complete.",
        "The current chat and previously committed canonical memory remain preserved.",
        "Inspect the visible review detail before repeating an enabled review action.",
        "Knowledge review state and the visible review items contain the failure context.",
    ),
    FailureTarget(
        "canonicalMemoryTabs",
        "canonical memory tabs",
        "The latest canonical-memory operation did not complete.",
        "The last successfully loaded Knowledge, Claims and decisions remain unchanged.",
        "Use Refresh Knowledge to request the current canonical view again.",
        "The Knowledge status and selected canonical detail pane retain the error output.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "persistentKnowledgeList",
        "canonical knowledge list",
        "The latest canonical Knowledge list request failed.",
        "Already persisted Knowledge is not removed or rewritten by a failed list request.",
        "Use Refresh Knowledge to reload the list from the existing canonical service.",
        "Knowledge browser status contains the request failure; selection stays local UI state.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "persistentKnowledgeDetails",
        "canonical knowledge details",
        "The selected Knowledge detail could not be loaded or refreshed.",
        "The canonical Knowledge entity and its stored revisions remain unchanged.",
        "Refresh Knowledge, then reselect the entity if the detail remains unavailable.",
        "The detail pane and Knowledge browser status contain the visible failure context.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "persistentClaimList",
        "canonical claim list",
        "The latest canonical Claim list request failed.",
        "Persisted Claims and their evidence links remain unchanged by the failed read.",
        "Use Refresh Knowledge while the Claims tab is selected.",
        "Knowledge browser status and the Claims surface retain the visible failure context.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "persistentClaimDetails",
        "canonical claim details",
        "The selected Claim detail could not be loaded or refreshed.",
        "The persisted Claim, evidence and revision history remain unchanged.",
        "Refresh the Claims tab and reselect the Claim if necessary.",
        "The Claim detail pane and Knowledge status contain the failure context.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "semanticReviewList",
        "semantic decision list",
        "The pending contradiction-decision view could not be refreshed.",
        "Pending decisions remain pending until an explicit reviewed action succeeds.",
        "Refresh Knowledge on the decisions tab before making another decision.",
        "The review list, selected detail and Knowledge status retain the error context.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "semanticReviewDetails",
        "semantic decision details",
        "The selected contradiction decision could not be loaded or resolved.",
        "No decision is assumed committed when the UI reports an error.",
        "Refresh the decision list and verify the pending state before retrying an action.",
        "The decision detail keeps both claims and the visible operation result available.",
        "knowledgeWorkspace",
        "refresh_knowledge_button",
    ),
    FailureTarget(
        "researchStatus",
        "research status",
        "The latest Research workspace operation did not complete.",
        "Existing durable research jobs and persisted work remain available.",
        "Use Refresh Research to request current durable research state.",
        "Research status and the selected run detail contain the visible failure context.",
        "researchWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "researchJobList",
        "research job list",
        "The durable research-job list could not be refreshed.",
        "Existing research runs continue under durable job state outside this failed read.",
        "Use Refresh Research before acting on an apparently stale run.",
        "Research status and the selected job detail contain the failure context.",
        "researchWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "researchDetails",
        "research details",
        "The selected research-run detail could not be loaded or updated.",
        "The durable research run is not cancelled or rewritten by a failed detail read.",
        "Refresh Research and reselect the run before making a lifecycle decision.",
        "The research detail pane retains command or controller failure information.",
        "researchWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "jobsStatus",
        "durable jobs status",
        "The latest durable Jobs workspace operation did not complete.",
        "Persisted job state remains authoritative despite the failed UI operation.",
        "Use Refresh Jobs to request the current scheduler-backed state again.",
        "Jobs status and selected job detail retain the visible failure context.",
        "jobsWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "schedulerStatus",
        "scheduler status",
        "Scheduler status could not be refreshed or represented successfully.",
        "The failed status read does not itself change scheduler or job state.",
        "Use Refresh Jobs before relying on lifecycle controls.",
        "Scheduler status and durable job detail contain the visible failure context.",
        "jobsWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "durableJobList",
        "durable job list",
        "The durable job list could not be refreshed.",
        "Existing jobs continue according to persisted scheduler state.",
        "Use Refresh Jobs before Pause, Resume, Wake or Cancel when the list is stale.",
        "Jobs status and selected job detail retain the failure context.",
        "jobsWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "jobDetails",
        "durable job details",
        "The selected durable job detail could not be loaded or updated.",
        "No lifecycle transition is inferred from a failed detail operation.",
        "Refresh Jobs and verify the current persisted state before another action.",
        "The job detail pane contains checkpoint, lease or operation failure information.",
        "jobsWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "sourceStatus",
        "source status",
        "The latest Source import or processing operation did not complete.",
        "Captured Source identity and previously persisted bytes remain explicit local state.",
        "Inspect Source details; use Process Source only when the existing control is enabled.",
        "Source status and Source details retain the processing or command failure context.",
        "filesWorkspace",
        "process_button",
    ),
    FailureTarget(
        "sourceList",
        "source list",
        "The Source list or its latest processing refresh did not complete.",
        "Already captured Sources remain local and are not removed by a failed list operation.",
        "Inspect the selected Source and use the existing Process action only if eligible.",
        "Source status and selected Source details retain the visible failure information.",
        "filesWorkspace",
        "process_button",
    ),
    FailureTarget(
        "sourceDetails",
        "source details",
        "The selected Source detail or processing operation failed.",
        "The Source record remains preserved unless an explicit successful operation says otherwise.",
        "Use Process Source for an eligible retry; otherwise retain the visible error for inspection.",
        "The Source detail pane is the primary location for processing failure output.",
        "filesWorkspace",
        "process_button",
    ),
    FailureTarget(
        "systemDetail",
        "system runtime detail",
        "The local runtime status snapshot could not be refreshed completely.",
        "A failed status read does not modify Core, model or persisted domain data.",
        "Use Refresh System after checking the local Core or model provider externally.",
        "System detail contains the last visible connection or runtime failure information.",
        "systemWorkspace",
        "refresh_button",
    ),
    FailureTarget(
        "backupSnapshotList",
        "backup snapshot list",
        "The latest BackupService-backed operation did not complete.",
        "Existing snapshots and the live runtime remain unchanged unless success is reported.",
        "Use Refresh to reload snapshots; inspect Backup details before retrying another operation.",
        "Backup status and details retain command output and the selected snapshot context.",
        "backupWorkspace",
        "refresh_button",
    ),
)

_DIMENSIONS: tuple[str, ...] = (
    "failure meaning",
    "preserved-state explanation",
    "existing recovery path",
    "failure evidence location",
    "assistive recovery state",
)

UI_REFINEMENT_TASKS_4301_4400: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_FAILURE_STYLESHEET = """
/* pATHENA failure recovery 4400 */
QWidget[pathenaFailureActive="true"] {
    border-color: #713C38;
}
QPushButton[pathenaRecoveryAction="true"] {
    border-color: #8A5A42;
}
"""


class FailureRecoveryController(QObject):
    """Explain existing error states without inventing retry behavior."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._targets: dict[QWidget, FailureTarget] = {}
        self._actions: dict[QWidget, QAbstractButton | None] = {}
        self._action_members: dict[QAbstractButton, set[QWidget]] = {}
        self._baseline: dict[QWidget, tuple[str, str]] = {}

    def register(
        self,
        widget: QWidget,
        target: FailureTarget,
        action: QAbstractButton | None,
    ) -> None:
        self._targets[widget] = target
        self._actions[widget] = action
        self._baseline[widget] = (widget.statusTip(), widget.accessibleDescription())
        if action is not None:
            self._action_members.setdefault(action, set()).add(widget)
        widget.installEventFilter(self)
        self._sync(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            isinstance(watched, QWidget)
            and isinstance(event, QDynamicPropertyChangeEvent)
            and bytes(event.propertyName().data()) == b"pathenaUiState"
        ):
            self._sync(watched)
        return super().eventFilter(watched, event)

    def _sync(self, widget: QWidget) -> None:
        target = self._targets[widget]
        active = str(widget.property("pathenaUiState")) == "error"
        previous = bool(widget.property("pathenaFailureActive"))

        widget.setProperty("pathenaFailureMeaning", target.failure)
        widget.setProperty("pathenaFailurePreserved", target.preserved)
        widget.setProperty("pathenaFailureRecovery", target.recovery)
        widget.setProperty("pathenaFailureEvidence", target.evidence)
        widget.setProperty("pathenaFailureActive", active)

        if active:
            widget.setStatusTip(
                f"{target.failure} Preserved: {target.preserved} Recovery: {target.recovery}"
            )
            widget.setAccessibleDescription(
                f"{target.label.capitalize()} error. {target.failure} "
                f"{target.preserved} {target.recovery} Evidence: {target.evidence}"
            )
        else:
            status_tip, accessible = self._baseline[widget]
            widget.setStatusTip(status_tip)
            widget.setAccessibleDescription(accessible)

        action = self._actions.get(widget)
        if action is not None:
            self._sync_action(action)

        if previous != active:
            self._repolish(widget)

    def _sync_action(self, action: QAbstractButton) -> None:
        members = self._action_members.get(action, set())
        active_members = tuple(
            widget
            for widget in members
            if bool(widget.property("pathenaFailureActive"))
        )
        active = bool(active_members)
        changed = bool(action.property("pathenaRecoveryAction")) != active
        action.setProperty("pathenaRecoveryAction", active)
        action.setProperty(
            "pathenaRecoveryFor",
            ";".join(sorted(widget.objectName() for widget in active_members)),
        )
        if changed:
            self._repolish(action)

    @staticmethod
    def _repolish(widget: QWidget) -> None:
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()


def _resolve_action(
    window: QWidget,
    target: FailureTarget,
) -> QAbstractButton | None:
    if target.recovery_workspace is None or target.recovery_attribute is None:
        return None
    workspace = window.findChild(QWidget, target.recovery_workspace)
    if workspace is None:
        return None
    candidate = getattr(workspace, target.recovery_attribute, None)
    return candidate if isinstance(candidate, QAbstractButton) else None


def apply_ui_refinements_4301_4400(window: QWidget) -> tuple[int, ...]:
    """Apply 100 failure-comprehension outcomes to existing semantic state surfaces."""
    controller = FailureRecoveryController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        controller.register(widget, target, _resolve_action(window, target))
        start = 4301 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    if _FAILURE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_FAILURE_STYLESHEET}")

    window.setProperty("pathenaFailureRecoveryController", controller)
    window.setProperty(
        "pathenaFailureRecoveryTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaFailureRecoveryTaskCount", len(applied))
    return tuple(applied)
