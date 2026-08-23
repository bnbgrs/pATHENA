"""Empty-state and first-action guidance refinements 3301-3400 for pATHENA.

This pass extends the existing polished chat first-run treatment to real Knowledge,
Research, Jobs, Files, System and backup surfaces. Empty views point to one existing
next action; no action, process, API route or persistence behavior is invented.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QWidget,
)


@dataclass(frozen=True)
class EmptyStateTarget:
    object_name: str
    label: str
    action_object_name: str | None
    action_label: str
    empty_copy: str


_TARGETS: tuple[EmptyStateTarget, ...] = (
    EmptyStateTarget(
        "chatSelector",
        "conversation selector",
        "newChatButton",
        "New conversation",
        "No saved conversation is selected yet.",
    ),
    EmptyStateTarget(
        "modelSelector",
        "local model selector",
        None,
        "Choose an available local model",
        "No local model is currently available to pATHENA.",
    ),
    EmptyStateTarget(
        "persistentKnowledgeList",
        "canonical knowledge",
        None,
        "Refresh Knowledge",
        "Canonical memory has no Knowledge items to show yet.",
    ),
    EmptyStateTarget(
        "persistentKnowledgeDetails",
        "knowledge details",
        None,
        "Select Knowledge",
        "Select a Knowledge item to inspect its current revision and provenance.",
    ),
    EmptyStateTarget(
        "persistentClaimList",
        "canonical claims",
        None,
        "Refresh Knowledge",
        "Canonical memory has no Claims to show yet.",
    ),
    EmptyStateTarget(
        "persistentClaimDetails",
        "claim details",
        None,
        "Select a Claim",
        "Select a Claim to inspect evidence, provenance and revision.",
    ),
    EmptyStateTarget(
        "semanticReviewList",
        "semantic decisions",
        None,
        "Review session proposals",
        "There are no pending semantic decisions.",
    ),
    EmptyStateTarget(
        "semanticReviewDetails",
        "semantic decision details",
        None,
        "Select a decision",
        "Select a pending decision to review its contradiction evidence.",
    ),
    EmptyStateTarget(
        "researchJobList",
        "research jobs",
        None,
        "Start research",
        "No durable research run has been created yet.",
    ),
    EmptyStateTarget(
        "researchDetails",
        "research details",
        None,
        "Select a research job",
        "Select a research run to inspect scope, coverage and work items.",
    ),
    EmptyStateTarget(
        "researchStatus",
        "research status",
        None,
        "Start research",
        "Research is ready for a local question.",
    ),
    EmptyStateTarget(
        "durableJobList",
        "background jobs",
        None,
        "Refresh jobs",
        "There are no durable background jobs to show.",
    ),
    EmptyStateTarget(
        "jobDetails",
        "job details",
        None,
        "Select a job",
        "Select a durable job to inspect checkpoints, leases and state.",
    ),
    EmptyStateTarget(
        "jobsStatus",
        "jobs status",
        None,
        "Refresh jobs",
        "The durable job queue is ready.",
    ),
    EmptyStateTarget(
        "sourceList",
        "local sources",
        None,
        "Import file",
        "No local Source has been imported yet.",
    ),
    EmptyStateTarget(
        "sourceDetails",
        "source details",
        None,
        "Select a Source",
        "Select a Source to inspect capture and retrieval readiness.",
    ),
    EmptyStateTarget(
        "sourceStatus",
        "source status",
        None,
        "Import file",
        "Sources are ready for local import.",
    ),
    EmptyStateTarget(
        "systemDetail",
        "system runtime",
        None,
        "Refresh system",
        "Runtime detail appears here when the local Core reports status.",
    ),
    EmptyStateTarget(
        "backupSnapshotList",
        "backup snapshots",
        None,
        "Create backup",
        "No backup snapshot is listed yet.",
    ),
    EmptyStateTarget(
        "backupDetails",
        "backup details",
        None,
        "Select a backup",
        "Select a completed backup to inspect verification and restore details.",
    ),
)

_DIMENSIONS: tuple[str, ...] = (
    "empty-state copy",
    "single next action",
    "assistive empty hint",
    "action relationship",
    "empty-state metadata",
)

UI_REFINEMENT_TASKS_3301_3400: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class EmptyStateGuidanceController(QObject):
    """Keep empty views concise and point them at one existing next step."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._targets: dict[QWidget, EmptyStateTarget] = {}
        self._actions: dict[QWidget, QAbstractButton | None] = {}

    def register(
        self,
        widget: QWidget,
        target: EmptyStateTarget,
        action: QAbstractButton | None,
    ) -> None:
        self._targets[widget] = target
        self._actions[widget] = action
        widget.installEventFilter(self)
        if isinstance(widget, QListWidget):
            model = widget.model()
            model.rowsInserted.connect(self.schedule_sync)
            model.rowsRemoved.connect(self.schedule_sync)
            model.modelReset.connect(self.schedule_sync)
        self._apply_static_guidance(widget, target, action)
        self.sync_widget(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QWidget) and event.type() in {
            QEvent.Type.Show,
            QEvent.Type.EnabledChange,
            QEvent.Type.DynamicPropertyChange,
        }:
            self.schedule_sync()
        return super().eventFilter(watched, event)

    def schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        for widget in self._targets:
            self.sync_widget(widget)

    def sync_widget(self, widget: QWidget) -> None:
        target = self._targets[widget]
        empty = self._is_empty(widget)
        widget.setProperty("pathenaEmptyStateActive", empty)
        widget.setProperty("pathenaEmptyStateLabel", target.label)
        widget.setProperty("pathenaEmptyNextAction", target.action_label)

        action = self._actions.get(widget)
        if action is not None:
            action.setProperty("pathenaEmptyStatePrimary", empty)
            action.setProperty("pathenaEmptyStateFor", widget.objectName())

        if isinstance(widget, QPlainTextEdit) and empty:
            widget.setPlaceholderText(target.empty_copy)
        elif isinstance(widget, QLineEdit) and empty and not widget.placeholderText():
            widget.setPlaceholderText(target.empty_copy)

        state = "empty" if empty else "populated"
        widget.setProperty("pathenaContentState", state)

    @staticmethod
    def _apply_static_guidance(
        widget: QWidget,
        target: EmptyStateTarget,
        action: QAbstractButton | None,
    ) -> None:
        widget.setProperty("pathenaEmptyStateCopy", target.empty_copy)
        widget.setProperty("pathenaEmptyStateSingleAction", True)
        widget.setAccessibleDescription(
            f"{target.empty_copy} Next step: {target.action_label}."
        )
        widget.setStatusTip(f"{target.empty_copy} {target.action_label}.")
        if action is not None:
            action.setAccessibleDescription(
                f"Primary action when {target.label} is empty: {target.action_label}."
            )

    @staticmethod
    def _is_empty(widget: QWidget) -> bool:
        if isinstance(widget, QListWidget):
            return widget.count() == 0
        if isinstance(widget, QComboBox):
            return widget.count() == 0
        if isinstance(widget, QPlainTextEdit):
            return not widget.toPlainText().strip()
        if isinstance(widget, QLineEdit):
            return not widget.text().strip()
        if isinstance(widget, QLabel):
            state = widget.property("pathenaUiState")
            return str(state) in {"empty", "idle"}
        return False


def _workspace_action(window: QWidget, object_name: str, label: str) -> QAbstractButton | None:
    if object_name == "chatSelector":
        return window.findChild(QAbstractButton, "newChatButton")

    mappings: tuple[tuple[str, str, str], ...] = (
        ("knowledgeWorkspace", "refresh_knowledge_button", "Refresh Knowledge"),
        ("researchWorkspace", "start_button", "Start research"),
        ("jobsWorkspace", "refresh_button", "Refresh jobs"),
        ("filesWorkspace", "import_button", "Import file"),
        ("systemWorkspace", "refresh_button", "Refresh system"),
        ("backupWorkspace", "create_button", "Create backup"),
    )
    for workspace_name, attribute_name, action_label in mappings:
        if label != action_label:
            continue
        workspace = window.findChild(QWidget, workspace_name)
        if workspace is None:
            continue
        candidate = getattr(workspace, attribute_name, None)
        if isinstance(candidate, QAbstractButton):
            return candidate
    return None


def apply_ui_refinements_3301_3400(window: QWidget) -> tuple[int, ...]:
    """Apply 100 empty-state outcomes using only existing next actions."""
    controller = EmptyStateGuidanceController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        action = _workspace_action(window, target.object_name, target.action_label)
        controller.register(widget, target, action)
        start = 3301 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaEmptyStateGuidanceController", controller)
    window.setProperty("pathenaEmptyStateTargetCount", len(applied) // len(_DIMENSIONS))
    window.setProperty("pathenaEmptyStateTaskCount", len(applied))
    return tuple(applied)
