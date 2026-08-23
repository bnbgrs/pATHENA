"""Truthful action-enablement rationale for pATHENA desktop controls.

Existing workspaces already own every enabled/disabled transition. This presentation-
only controller observes those real states and explains why a disabled control is not
currently actionable and what existing condition makes it available again. It never
calls setEnabled(), starts work, changes selection or invents a backend capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class EnablementTarget:
    workspace_name: str | None
    attribute_name: str
    label: str
    kind: str


_TARGETS: tuple[EnablementTarget, ...] = (
    EnablementTarget(None, "prompt_input", "Chat composer", "chat-compose"),
    EnablementTarget(None, "ground_button", "Grounding", "chat-compose"),
    EnablementTarget(None, "send_button", "Send", "chat-compose"),
    EnablementTarget(None, "model_selector", "Model selector", "chat-model"),
    EnablementTarget(None, "delete_chat_button", "Delete conversation", "chat-delete"),
    EnablementTarget("researchWorkspace", "query_input", "Research query", "research-basic"),
    EnablementTarget("researchWorkspace", "start_button", "Start research", "research-basic"),
    EnablementTarget("researchWorkspace", "refresh_button", "Refresh research", "research-basic"),
    EnablementTarget("researchWorkspace", "cancel_button", "Cancel research", "research-cancel"),
    EnablementTarget("jobsWorkspace", "refresh_button", "Refresh jobs", "jobs-refresh"),
    EnablementTarget("jobsWorkspace", "pause_button", "Pause job", "jobs-pause"),
    EnablementTarget("jobsWorkspace", "resume_button", "Resume job", "jobs-resume"),
    EnablementTarget("jobsWorkspace", "wake_button", "Wake job", "jobs-wake"),
    EnablementTarget("jobsWorkspace", "cancel_button", "Cancel job", "jobs-cancel"),
    EnablementTarget("filesWorkspace", "import_button", "Import file", "files-basic"),
    EnablementTarget("filesWorkspace", "refresh_button", "Refresh Sources", "files-basic"),
    EnablementTarget("filesWorkspace", "process_button", "Process Source", "files-process"),
    EnablementTarget("backupWorkspace", "create_button", "Create backup", "backup-basic"),
    EnablementTarget("backupWorkspace", "verify_button", "Verify backup", "backup-selected"),
    EnablementTarget("backupWorkspace", "restore_button", "Restore isolated", "backup-selected"),
)

_DIMENSIONS: tuple[str, ...] = (
    "disabled reason",
    "restore condition",
    "accessible availability rationale",
    "tooltip availability rationale",
    "enablement diagnostic metadata",
)

UI_REFINEMENT_TASKS_5601_5700: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_JOB_ELIGIBILITY: dict[str, frozenset[str]] = {
    "jobs-pause": frozenset({"queued", "waiting"}),
    "jobs-resume": frozenset({"paused"}),
    "jobs-wake": frozenset({"waiting"}),
}
_TERMINAL_JOB_STATES = frozenset({"cancelled", "failed", "completed", "cancel_requested"})
_ACTIVE_SOURCE_STATES = frozenset({"queued", "waiting", "running", "paused", "cancel_requested"})


class EnablementRationaleController(QObject):
    """Explain existing disabled states without becoming an enablement owner."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._targets: list[tuple[QWidget, QWidget, EnablementTarget]] = []
        self._last: dict[QWidget, tuple[bool, str, str]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(
        self,
        workspace: QWidget,
        widget: QWidget,
        target: EnablementTarget,
    ) -> None:
        self._targets.append((workspace, widget, target))
        widget.installEventFilter(self)
        widget.setProperty("pathenaEnablementObservedOnly", True)
        self._sync_one(workspace, widget, target)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QWidget) and event.type() == QEvent.Type.EnabledChange:
            QTimer.singleShot(0, self.sync)
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        for workspace, widget, target in self._targets:
            self._sync_one(workspace, widget, target)

    def _sync_one(
        self,
        workspace: QWidget,
        widget: QWidget,
        target: EnablementTarget,
    ) -> None:
        reason, restore = self._rationale(workspace, widget, target.kind)
        signature = (widget.isEnabled(), reason, restore)
        if self._last.get(widget) == signature:
            return
        self._last[widget] = signature

        available = widget.isEnabled()
        reason_text = "Available now." if available else reason
        restore_text = "No prerequisite is currently blocking this control." if available else restore

        widget.setProperty("pathenaEnablementAvailable", available)
        widget.setProperty("pathenaEnablementReason", reason_text)
        widget.setProperty("pathenaEnablementRestoreCondition", restore_text)
        widget.setProperty("pathenaEnablementRationaleSynchronized", True)

        availability = f"Availability: {reason_text} {restore_text}"
        widget.setAccessibleDescription(
            self._with_suffix(widget.accessibleDescription(), " Availability: ", availability)
        )
        widget.setToolTip(self._with_suffix(widget.toolTip(), "\nAvailability: ", availability))
        widget.setStatusTip(availability)

    def _rationale(
        self,
        workspace: QWidget,
        widget: QWidget,
        kind: str,
    ) -> tuple[str, str]:
        if kind.startswith("chat-"):
            return self._chat_rationale(widget, kind)
        if kind.startswith("research-"):
            return self._research_rationale(workspace, kind)
        if kind.startswith("jobs-"):
            return self._jobs_rationale(workspace, kind)
        if kind.startswith("files-"):
            return self._files_rationale(workspace, kind)
        if kind.startswith("backup-"):
            return self._backup_rationale(workspace, kind)
        return (
            "Unavailable in the current UI state.",
            "Wait for the owning workspace to become actionable.",
        )

    def _chat_rationale(self, widget: QWidget, kind: str) -> tuple[str, str]:
        if getattr(self.window, "api_controller", None) is None:
            return (
                "The desktop API controller is unavailable.",
                "The control returns when the local desktop controller is connected.",
            )
        if bool(getattr(self.window, "_chat_busy", False)):
            return (
                "A chat operation is still running.",
                "Wait for the current chat operation to finish.",
            )
        if getattr(self.window, "pending_chat_id", None) is not None:
            return (
                "A selected conversation is still loading.",
                "Wait for the conversation selection to finish loading.",
            )
        if kind == "chat-compose" and not bool(getattr(self.window, "_core_ready", False)):
            return (
                "The local Core, provider and selected model are not ready for chat.",
                "Chat becomes available when the existing readiness checks report ready.",
            )
        if kind == "chat-model" and hasattr(widget, "count"):
            count = getattr(widget, "count")
            if isinstance(count, Callable) and count() == 0:
                return (
                    "No local model is currently listed.",
                    "The selector becomes available when model discovery returns a model.",
                )
        if kind == "chat-delete" and getattr(self.window, "current_chat_id", None) is None:
            return (
                "There is no persisted current conversation to delete.",
                "Select an existing persisted conversation first.",
            )
        return (
            "Unavailable under the current chat readiness state.",
            "The control returns when its existing chat prerequisite is satisfied.",
        )

    @staticmethod
    def _research_rationale(workspace: QWidget, kind: str) -> tuple[str, str]:
        if _is_busy(workspace):
            return (
                "A local research command is running.",
                "Wait for the current research command to finish.",
            )
        if kind == "research-cancel" and not getattr(workspace, "_selected_job_id", None):
            return (
                "No research job is selected.",
                "Select a research job to make cancellation available.",
            )
        return (
            "Unavailable under the current research state.",
            "The control returns when its existing research prerequisite is satisfied.",
        )

    @staticmethod
    def _jobs_rationale(workspace: QWidget, kind: str) -> tuple[str, str]:
        if _is_busy(workspace):
            return (
                "A durable-job command is running.",
                "Wait for the current durable-job command to finish.",
            )
        if kind == "jobs-refresh":
            return (
                "Refresh is temporarily unavailable.",
                "Refresh returns when the current workspace operation is idle.",
            )
        state_value = getattr(workspace, "_selected_state", None)
        state = str(state_value) if state_value else ""
        if not state:
            return (
                "No durable job is selected.",
                "Select a durable job to evaluate this transition.",
            )
        eligible = _JOB_ELIGIBILITY.get(kind)
        if eligible is not None and state not in eligible:
            expected = ", ".join(sorted(eligible))
            return (
                f"The selected job state is {state}; this transition is not eligible.",
                f"This action is available only for job state: {expected}.",
            )
        if kind == "jobs-cancel" and state in _TERMINAL_JOB_STATES:
            return (
                f"The selected job state is {state}; cancellation is no longer actionable.",
                "Select a non-terminal job without an existing cancellation request.",
            )
        return (
            "Unavailable for the selected durable-job state.",
            "Select a job whose existing state permits this transition.",
        )

    @staticmethod
    def _files_rationale(workspace: QWidget, kind: str) -> tuple[str, str]:
        if _is_busy(workspace):
            return (
                "A Source command is running.",
                "Wait for the current Source command to finish.",
            )
        if kind != "files-process":
            return (
                "The Source workspace is temporarily unavailable.",
                "The control returns when the Source workspace is idle.",
            )
        if not getattr(workspace, "_selected_source_id", None):
            return (
                "No Source is selected.",
                "Select a Source to evaluate processing readiness.",
            )
        if not bool(getattr(workspace, "_selected_processable", False)):
            return (
                "The selected Source is not processable by the existing pipeline.",
                "Select a Source supported by the existing processing pipeline.",
            )
        readiness_value = getattr(workspace, "_selected_readiness", None)
        readiness = str(readiness_value) if readiness_value else ""
        if readiness == "ready":
            return (
                "The selected Source is already retrieval-ready.",
                "Select a Source that still requires processing or retry.",
            )
        if readiness in _ACTIVE_SOURCE_STATES:
            return (
                f"The selected Source already has active state {readiness}.",
                "Wait for the active processing state to settle before retrying.",
            )
        return (
            "Processing is unavailable for the selected Source.",
            "Select a processable Source that is not already ready or active.",
        )

    @staticmethod
    def _backup_rationale(workspace: QWidget, kind: str) -> tuple[str, str]:
        if _is_busy(workspace):
            return (
                "A backup operation is running.",
                "Wait for the current backup operation to finish.",
            )
        if kind == "backup-selected" and not getattr(workspace, "_selected_snapshot_id", None):
            return (
                "No backup snapshot is selected.",
                "Select a backup snapshot first.",
            )
        return (
            "The backup action is temporarily unavailable.",
            "The control returns when its existing backup prerequisite is satisfied.",
        )

    @staticmethod
    def _with_suffix(current: str, marker: str, suffix: str) -> str:
        base = current.split(marker, 1)[0].rstrip()
        if not base:
            return suffix
        return f"{base}{marker}{suffix}"


def _is_busy(workspace: QWidget) -> bool:
    candidate = getattr(workspace, "_busy", None)
    return bool(candidate()) if callable(candidate) else False


def _resolve(window: QWidget, target: EnablementTarget) -> tuple[QWidget, QWidget] | None:
    workspace = window
    if target.workspace_name is not None:
        found = window.findChild(QWidget, target.workspace_name)
        if found is None:
            return None
        workspace = found
    widget = getattr(workspace, target.attribute_name, None)
    if isinstance(widget, QWidget):
        return workspace, widget
    return None


def apply_ui_refinements_5601_5700(window: QWidget) -> tuple[int, ...]:
    """Install truthful disabled-state rationale without owning enablement."""
    controller = EnablementRationaleController(window)
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        resolved = _resolve(window, target)
        if resolved is None:
            continue
        workspace, widget = resolved
        controller.register(workspace, widget, target)
        start = 5601 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaEnablementRationaleController", controller)
    window.setProperty("pathenaEnablementRationaleManaged", True)
    return tuple(applied)
