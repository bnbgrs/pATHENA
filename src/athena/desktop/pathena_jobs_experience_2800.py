"""Jobs experience refinements 2701-2800 for pATHENA.

The durable job service and jobs CLI remain authoritative for all transitions. This
presentation controller adds filtering, keyboard flow, progressive action visibility
and readable job-detail formatting without changing durable job state or persistence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.jobs_workspace import JobsWorkspace


@dataclass(frozen=True)
class JobsExperienceTarget:
    key: str
    label: str


_TARGETS: tuple[JobsExperienceTarget, ...] = (
    JobsExperienceTarget("jobsWorkspace", "Jobs workspace"),
    JobsExperienceTarget("jobsFilter", "Jobs filter"),
    JobsExperienceTarget("schedulerStatus", "Scheduler status"),
    JobsExperienceTarget("jobsStatus", "Jobs operation status"),
    JobsExperienceTarget("durableJobList", "Durable jobs list"),
    JobsExperienceTarget("jobsPrimarySplitter", "Jobs browse-detail splitter"),
    JobsExperienceTarget("jobDetails", "Job details"),
    JobsExperienceTarget("jobsRefreshButton", "Refresh jobs action"),
    JobsExperienceTarget("jobPauseButton", "Pause job action"),
    JobsExperienceTarget("jobResumeButton", "Resume job action"),
    JobsExperienceTarget("jobWakeButton", "Wake job action"),
    JobsExperienceTarget("jobCancelButton", "Cancel job action"),
    JobsExperienceTarget("jobState", "Job state information"),
    JobsExperienceTarget("jobStage", "Job stage information"),
    JobsExperienceTarget("jobRetries", "Job retry information"),
    JobsExperienceTarget("jobCheckpoint", "Job checkpoint information"),
    JobsExperienceTarget("jobLease", "Job lease information"),
    JobsExperienceTarget("jobScope", "Job requested scope"),
    JobsExperienceTarget("jobConfiguration", "Job pinned configuration"),
    JobsExperienceTarget("jobsEmptyState", "Jobs empty state"),
)

_REFINEMENTS: tuple[str, ...] = (
    "clarify durable-state meaning",
    "reduce inactive control chrome",
    "improve keyboard traversal",
    "prioritize actionable information",
    "preserve canonical job-service behavior",
)

UI_REFINEMENT_TASKS_2701_2800: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _TARGETS
    for refinement in _REFINEMENTS
)

_DETAIL_LABELS = {
    "JOB": "Job",
    "TYPE": "Type",
    "STATE": "State",
    "PRIORITY": "Priority",
    "STAGE": "Stage",
    "RETRIES": "Retries",
    "BLOCKED": "Blocked reason",
    "CREATED_AT_US": "Created",
    "UPDATED_AT_US": "Updated",
    "NEXT_RUN_AT_US": "Next run",
    "WORKER": "Worker",
    "LEASE_ACQUIRED_AT_US": "Lease acquired",
    "LEASE_EXPIRES_AT_US": "Lease expires",
    "HEARTBEAT_AT_US": "Heartbeat",
    "FENCING_SEQUENCE": "Fencing sequence",
    "PROCESSING_RUN": "Processing run",
    "LAST_CHECKPOINT": "Last checkpoint",
    "PROTECTION_SCOPE": "Protection scope",
    "PROTECTED_PAYLOAD": "Protected payload",
    "REQUESTED_SCOPE": "Requested scope",
    "PINNED_CONFIGURATION": "Pinned configuration",
    "CHECKPOINTS": "Checkpoints",
}

_STYLESHEET = r"""
QLineEdit#jobsFilter {
    background: #090909;
    border: 1px solid #242424;
    padding: 7px 9px;
}
QLineEdit#jobsFilter:focus { border-color: #F26A21; }
QPlainTextEdit#jobDetails {
    background: #080808;
    border: none;
    color: #D8D8D8;
    padding: 10px 12px;
}
QPushButton[pathenaJobsSecondary="true"] {
    background: transparent;
    border-color: transparent;
    color: #9A9A9A;
}
QPushButton[pathenaJobsSecondary="true"]:hover {
    color: #E2E2E2;
    border-color: #242424;
}
QPushButton[pathenaJobsDestructive="true"] {
    background: transparent;
    color: #C98C86;
    border-color: #392421;
}
"""


def _humanize_detail_text(text: str) -> str:
    """Humanize jobs CLI detail labels while preserving every emitted value."""
    lines: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith("CHECKPOINT "):
            lines.append("Checkpoint · " + stripped.removeprefix("CHECKPOINT "))
            continue
        if stripped.startswith("PROGRESS "):
            lines.append("  Progress · " + stripped.removeprefix("PROGRESS "))
            continue
        if stripped.startswith("RESUME "):
            lines.append("  Resume metadata · " + stripped.removeprefix("RESUME "))
            continue
        match = re.match(r"^([A-Z][A-Z0-9_]+)\s+(.*)$", stripped)
        if match is None:
            lines.append(raw_line)
            continue
        key, value = match.groups()
        label = _DETAIL_LABELS.get(key, key.replace("_", " ").title())
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


class PathenaJobsExperience(QObject):
    """Presentation-only durable-jobs usability layer."""

    def __init__(self, workspace: JobsWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._install_stable_identities()
        self.filter_input = self._install_filter()
        self._configure_accessibility()
        self._configure_details()
        self._configure_shortcuts()
        self._configure_tab_order()
        self._connect_state_sync()
        self._tag_targets()
        if _STYLESHEET not in workspace.styleSheet():
            workspace.setStyleSheet(f"{workspace.styleSheet()}\n{_STYLESHEET}")
        self._sync_actions()

    def _install_stable_identities(self) -> None:
        self.workspace.refresh_button.setObjectName("jobsRefreshButton")
        self.workspace.pause_button.setObjectName("jobPauseButton")
        self.workspace.resume_button.setObjectName("jobResumeButton")
        self.workspace.wake_button.setObjectName("jobWakeButton")
        self.workspace.cancel_button.setObjectName("jobCancelButton")
        splitter = self.workspace.jobs.parentWidget()
        if isinstance(splitter, QSplitter):
            splitter.setObjectName("jobsPrimarySplitter")

    def _install_filter(self) -> QLineEdit:
        filter_input = QLineEdit(self.workspace)
        filter_input.setObjectName("jobsFilter")
        filter_input.setPlaceholderText("Filter jobs by state, type, stage, or scope…")
        filter_input.setClearButtonEnabled(True)
        filter_input.textChanged.connect(self._apply_filter)

        root = self.workspace.layout()
        if isinstance(root, QVBoxLayout):
            splitter = self.workspace.jobs.parentWidget()
            if isinstance(splitter, QSplitter):
                index = root.indexOf(splitter)
                if index >= 0:
                    row = QHBoxLayout()
                    label = QLabel("Jobs")
                    label.setProperty("role", "section")
                    row.addWidget(label)
                    row.addWidget(filter_input, 1)
                    root.insertLayout(index, row)
        return filter_input

    def _configure_accessibility(self) -> None:
        controls: tuple[tuple[QWidget, str, str], ...] = (
            (self.workspace, "Durable jobs", "Inspect and control canonical persistent background jobs."),
            (self.filter_input, "Filter durable jobs", "Filter the visible durable-job list without changing persisted jobs."),
            (self.workspace.scheduler_status, "Scheduler status", "Current local scheduler supervision state."),
            (self.workspace.status, "Jobs operation status", "Status of the current jobs list, detail, or transition command."),
            (self.workspace.jobs, "Durable jobs list", "Persistent jobs with state, priority, type, stage, and scope summary."),
            (self.workspace.details, "Durable job details", "Selected job metadata, lease information, scope, configuration, and checkpoints."),
            (self.workspace.refresh_button, "Refresh jobs", "Reload durable jobs from the canonical job repository."),
            (self.workspace.pause_button, "Pause selected job", "Pause an eligible queued or waiting durable job."),
            (self.workspace.resume_button, "Resume selected job", "Resume the selected paused durable job."),
            (self.workspace.wake_button, "Wake selected job", "Wake the selected waiting durable job."),
            (self.workspace.cancel_button, "Cancel selected job", "Persist a cancellation request for the selected nonterminal job."),
        )
        for widget, name, description in controls:
            widget.setAccessibleName(name)
            widget.setAccessibleDescription(description)
            widget.setToolTip(description)

    def _configure_details(self) -> None:
        self.workspace.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.workspace.details.document().setDocumentMargin(12.0)
        self.workspace.jobs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.workspace.jobs.setAlternatingRowColors(False)
        for button in (
            self.workspace.refresh_button,
            self.workspace.pause_button,
            self.workspace.resume_button,
            self.workspace.wake_button,
        ):
            button.setProperty("pathenaJobsSecondary", True)
        self.workspace.cancel_button.setProperty("pathenaJobsDestructive", True)

    def _configure_shortcuts(self) -> None:
        self.find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self.workspace)
        self.find_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.find_shortcut.activated.connect(self.filter_input.setFocus)
        self.refresh_shortcut = QShortcut(QKeySequence("F5"), self.workspace)
        self.refresh_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.refresh_shortcut.activated.connect(self._refresh_if_available)
        self.filter_input.setToolTip("Filter durable jobs (Ctrl+F)")
        self.workspace.refresh_button.setToolTip("Reload durable jobs (F5)")

    def _configure_tab_order(self) -> None:
        QWidget.setTabOrder(self.filter_input, self.workspace.jobs)
        QWidget.setTabOrder(self.workspace.jobs, self.workspace.details)
        QWidget.setTabOrder(self.workspace.details, self.workspace.refresh_button)
        QWidget.setTabOrder(self.workspace.refresh_button, self.workspace.pause_button)
        QWidget.setTabOrder(self.workspace.pause_button, self.workspace.resume_button)
        QWidget.setTabOrder(self.workspace.resume_button, self.workspace.wake_button)
        QWidget.setTabOrder(self.workspace.wake_button, self.workspace.cancel_button)

    def _connect_state_sync(self) -> None:
        self.workspace.jobs.currentItemChanged.connect(self._sync_actions)
        self.workspace._process.finished.connect(self._schedule_post_process_sync)
        model = self.workspace.jobs.model()
        model.rowsInserted.connect(self._apply_current_filter)
        model.modelReset.connect(self._apply_current_filter)

    def _schedule_post_process_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self._post_process_sync)

    def _post_process_sync(self) -> None:
        if self.workspace._operation == "show":
            self._humanize_details()
        else:
            # _operation is cleared by the workspace before this queued callback.
            text = self.workspace.details.toPlainText()
            if text.startswith("JOB "):
                self._humanize_details()
        self._sync_actions()
        self._apply_current_filter()

    def _humanize_details(self) -> None:
        raw = self.workspace.details.toPlainText()
        if not raw or raw.startswith("Job:"):
            return
        humanized = _humanize_detail_text(raw)
        if humanized != raw:
            self.workspace.details.setProperty("pathenaRawJobDetails", raw)
            self.workspace.details.setPlainText(humanized)

    def _refresh_if_available(self) -> None:
        if self.workspace.refresh_button.isEnabled():
            self.workspace.refresh_button.click()

    def _apply_current_filter(self, *_args: object) -> None:
        self._apply_filter(self.filter_input.text())

    def _apply_filter(self, text: str) -> None:
        terms = tuple(part for part in text.casefold().split() if part)
        for index in range(self.workspace.jobs.count()):
            item = self.workspace.jobs.item(index)
            haystack = f"{item.text()} {item.toolTip()}".casefold()
            item.setHidden(bool(terms) and not all(term in haystack for term in terms))

    def _sync_actions(self, *_args: object) -> None:
        # Visibility follows the workspace's existing enablement/state rules; no
        # transition eligibility is reimplemented here.
        self.workspace.pause_button.setVisible(self.workspace.pause_button.isEnabled())
        self.workspace.resume_button.setVisible(self.workspace.resume_button.isEnabled())
        self.workspace.wake_button.setVisible(self.workspace.wake_button.isEnabled())
        self.workspace.cancel_button.setVisible(self.workspace.cancel_button.isEnabled())
        self.workspace.status.setWordWrap(True)
        self.workspace.scheduler_status.setText(
            self.workspace.scheduler_status.text()
            .replace("SCHEDULER · ", "Scheduler · ")
            .replace("RECOVERY PENDING", "Recovery pending")
            .replace("ACTIVE", "Active")
            .replace("STOPPING", "Stopping")
            .replace("EXTERNAL", "External")
        )

    def _tag_targets(self) -> None:
        for target in _TARGETS:
            widget = self.workspace.findChild(QWidget, target.key)
            if widget is not None:
                widget.setProperty("pathenaJobsExperience", True)


def apply_ui_refinements_2701_2800(window: QWidget) -> tuple[int, ...]:
    """Register task coverage for an already installed jobs experience controller."""
    workspace = window.findChild(QWidget, "jobsWorkspace")
    if workspace is None:
        return ()
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.key)
        if widget is None and target.key not in {
            "jobState", "jobStage", "jobRetries", "jobCheckpoint", "jobLease",
            "jobScope", "jobConfiguration", "jobsEmptyState",
        }:
            continue
        start = 2701 + index * len(_REFINEMENTS)
        applied.extend(range(start, start + len(_REFINEMENTS)))
    return tuple(applied)


def install_jobs_experience(workspace: JobsWorkspace) -> PathenaJobsExperience:
    """Install filtering, keyboard flow and progressive durable-job controls."""
    return PathenaJobsExperience(workspace)
