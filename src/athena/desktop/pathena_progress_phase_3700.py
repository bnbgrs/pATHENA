"""Progress and long-running work refinements 3601-3700 for pATHENA.

The desktop already exposes real QProcess-backed work in Knowledge, Research, Jobs,
Files and Backup. This pass presents those existing operations as honest indeterminate
activity: operation/phase, busy ownership, expected result surface and completion
metadata. It never invents a percentage or changes process/domain behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QProcess, QTimer
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class ProgressTarget:
    workspace_name: str
    attribute_name: str | None
    object_name: str | None
    label: str
    result_surface: str


_TARGETS: tuple[ProgressTarget, ...] = (
    ProgressTarget("knowledgeWorkspace", "state", None, "knowledge state", "session review or canonical memory"),
    ProgressTarget("knowledgeWorkspace", "browser_status", None, "knowledge browser status", "selected canonical tab"),
    ProgressTarget("knowledgeWorkspace", "knowledge_details", None, "knowledge details", "knowledge details"),
    ProgressTarget("knowledgeWorkspace", "claim_details", None, "claim details", "claim details"),
    ProgressTarget("knowledgeWorkspace", "review_details", None, "decision details", "decision details"),
    ProgressTarget("researchWorkspace", "status", None, "research status", "research job list"),
    ProgressTarget("researchWorkspace", "jobs", None, "research jobs", "research job list"),
    ProgressTarget("researchWorkspace", "details", None, "research details", "research details"),
    ProgressTarget("researchWorkspace", "start_button", None, "research start", "research job list"),
    ProgressTarget("jobsWorkspace", "status", None, "jobs status", "durable job list"),
    ProgressTarget("jobsWorkspace", "scheduler_status", None, "scheduler status", "durable job list"),
    ProgressTarget("jobsWorkspace", "jobs", None, "durable jobs", "durable job list"),
    ProgressTarget("jobsWorkspace", "details", None, "job details", "job details"),
    ProgressTarget("filesWorkspace", "status", None, "source status", "source list"),
    ProgressTarget("filesWorkspace", "sources", None, "source list", "source list"),
    ProgressTarget("filesWorkspace", "details", None, "source details", "source details"),
    ProgressTarget("filesWorkspace", "process_button", None, "source processing", "source details"),
    ProgressTarget("backupWorkspace", "status", None, "backup status", "backup snapshot list"),
    ProgressTarget("backupWorkspace", "snapshots", None, "backup snapshots", "backup snapshot list"),
    ProgressTarget("backupWorkspace", "details", None, "backup details", "backup details"),
)

_DIMENSIONS: tuple[str, ...] = (
    "operation phase",
    "indeterminate progress truth",
    "busy ownership",
    "result destination",
    "completion metadata",
)

UI_REFINEMENT_TASKS_3601_3700: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class ProgressPhaseController(QObject):
    """Mirror real QProcess activity into quiet, non-fabricated progress metadata."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._targets: list[tuple[QWidget, QWidget, ProgressTarget]] = []
        self._previous_busy: dict[QWidget, bool] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, workspace: QWidget, widget: QWidget, target: ProgressTarget) -> None:
        self._targets.append((workspace, widget, target))
        self._previous_busy.setdefault(widget, False)
        self._sync_one(workspace, widget, target)

    def sync(self) -> None:
        for workspace, widget, target in self._targets:
            self._sync_one(workspace, widget, target)

    def _sync_one(self, workspace: QWidget, widget: QWidget, target: ProgressTarget) -> None:
        process = self._process_for(workspace)
        busy = process is not None and process.state() != QProcess.ProcessState.NotRunning
        operation = self._operation_for(workspace)
        previous = self._previous_busy.get(widget, False)

        widget.setProperty("pathenaOperationPhase", operation if busy else "idle")
        widget.setProperty("pathenaProgressMode", "indeterminate" if busy else "none")
        widget.setProperty("pathenaBusyOwner", workspace.objectName() if busy else "")
        widget.setProperty("pathenaProgressResultSurface", target.result_surface)
        widget.setProperty("pathenaLongRunningWork", busy)

        if previous and not busy:
            count = int(widget.property("pathenaOperationCompletionCount") or 0) + 1
            widget.setProperty("pathenaOperationCompletionCount", count)
            widget.setProperty("pathenaLastCompletedOperation", operation or "operation")
        self._previous_busy[widget] = busy

        if busy:
            widget.setStatusTip(
                f"Working: {operation or 'local operation'}. "
                f"Result appears in {target.result_surface}."
            )

    @staticmethod
    def _process_for(workspace: QWidget) -> QProcess | None:
        for attribute_name in ("_knowledge_process", "_process", "process"):
            candidate = getattr(workspace, attribute_name, None)
            if isinstance(candidate, QProcess):
                return candidate
        return None

    @staticmethod
    def _operation_for(workspace: QWidget) -> str:
        for attribute_name in ("_knowledge_operation", "_operation"):
            value = getattr(workspace, attribute_name, "")
            if isinstance(value, str) and value:
                return value.replace("-", " ")
        return ""


def _resolve(window: QWidget, target: ProgressTarget) -> tuple[QWidget, QWidget] | None:
    workspace = window.findChild(QWidget, target.workspace_name)
    if workspace is None:
        return None
    if target.attribute_name is not None:
        candidate = getattr(workspace, target.attribute_name, None)
        if isinstance(candidate, QWidget):
            return workspace, candidate
    if target.object_name is not None:
        candidate = workspace.findChild(QWidget, target.object_name)
        if candidate is not None:
            return workspace, candidate
    return None


def apply_ui_refinements_3601_3700(window: QWidget) -> tuple[int, ...]:
    """Apply 100 honest long-running-work outcomes to existing process surfaces."""
    controller = ProgressPhaseController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        resolved = _resolve(window, target)
        if resolved is None:
            continue
        workspace, widget = resolved
        controller.register(workspace, widget, target)
        start = 3601 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaProgressPhaseController", controller)
    window.setProperty("pathenaProgressPhaseTargetCount", len(applied) // len(_DIMENSIONS))
    window.setProperty("pathenaProgressPhaseTaskCount", len(applied))
    return tuple(applied)
