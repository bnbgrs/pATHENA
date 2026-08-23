"""Functional JOBS workspace for the native pATHENA desktop shell."""

from __future__ import annotations

import sys

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state
from athena.desktop.scheduler_supervisor import DesktopJobSchedulerSupervisor

_TERMINAL_STATES = frozenset({"cancelled", "failed", "completed"})
_PAUSABLE_STATES = frozenset({"queued", "waiting"})
_RESUMABLE_STATES = frozenset({"paused"})
_WAKEABLE_STATES = frozenset({"waiting"})


class JobsWorkspace(QWidget):
    """Observe and control the canonical durable job queue without blocking Qt."""

    def __init__(
        self,
        scheduler_supervisor: DesktopJobSchedulerSupervisor | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("jobsWorkspace")
        self._scheduler_supervisor = scheduler_supervisor
        self._operation = ""
        self._buffer = ""
        self._selected_job_id: str | None = None
        self._selected_state: str | None = None

        self.refresh_button = QPushButton("REFRESH")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.clicked.connect(self.refresh)

        self.pause_button = QPushButton("PAUSE")
        self.pause_button.setObjectName("newChatButton")
        self.pause_button.clicked.connect(self.pause_selected)

        self.resume_button = QPushButton("RESUME")
        self.resume_button.setObjectName("newChatButton")
        self.resume_button.clicked.connect(self.resume_selected)

        self.wake_button = QPushButton("WAKE")
        self.wake_button.setObjectName("newChatButton")
        self.wake_button.clicked.connect(self.wake_selected)

        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setObjectName("newChatButton")
        self.cancel_button.clicked.connect(self.cancel_selected)

        self.scheduler_status = QLabel()
        self.scheduler_status.setObjectName("schedulerStatus")
        self.scheduler_status.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        set_pathena_ui_state(self.scheduler_status, "idle")

        self.status = QLabel("Ready.")
        self.status.setObjectName("jobsStatus")
        self.status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        set_pathena_ui_state(self.status, "idle")

        self.jobs = QListWidget()
        self.jobs.setObjectName("durableJobList")
        self.jobs.setMinimumWidth(430)
        self.jobs.currentItemChanged.connect(self._selection_changed)
        set_pathena_ui_state(self.jobs, "idle")

        self.details = QPlainTextEdit()
        self.details.setObjectName("jobDetails")
        self.details.setReadOnly(True)
        self.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.details.setPlaceholderText(
            "Select a durable job to inspect checkpoints, leases and pinned state."
        )
        set_pathena_ui_state(self.details, "empty")

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._drain_output)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10_000)
        self._refresh_timer.timeout.connect(self._refresh_if_visible)
        self._refresh_timer.start()

        self._scheduler_status_timer = QTimer(self)
        self._scheduler_status_timer.setInterval(1_000)
        self._scheduler_status_timer.timeout.connect(self._refresh_scheduler_status)
        self._scheduler_status_timer.start()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("DURABLE JOB CONTROL")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addWidget(self.scheduler_status)
        header.addStretch(1)
        header.addWidget(self.refresh_button)
        header.addWidget(self.pause_button)
        header.addWidget(self.resume_button)
        header.addWidget(self.wake_button)
        header.addWidget(self.cancel_button)
        layout.addLayout(header)

        intro = QLabel(
            "Canonical pATHENA background work. Queue state, retries, leases and "
            "checkpoints are persisted in SQLite; controls below invoke the existing "
            "DurableJobService transitions rather than maintaining a GUI-side queue."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.jobs)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self._refresh_scheduler_status()
        self._sync_action_buttons()
        QTimer.singleShot(0, self.refresh)

    def refresh(self) -> None:
        if self._busy():
            return
        self._start("list", ["list", "--limit", "150"], "Refreshing durable jobs")

    def pause_selected(self) -> None:
        self._transition("pause", "Pausing selected job")

    def resume_selected(self) -> None:
        self._transition("resume", "Resuming selected job")

    def wake_selected(self) -> None:
        self._transition("wake", "Waking selected job")

    def cancel_selected(self) -> None:
        self._transition("cancel", "Persisting cancellation request")

    def _transition(self, operation: str, label: str) -> None:
        if self._busy() or not self._selected_job_id:
            return
        set_pathena_ui_state(self.details, "busy")
        self._start(operation, [operation, self._selected_job_id], label)

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        job_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        state = None if current is None else current.data(Qt.ItemDataRole.UserRole + 1)
        self._selected_job_id = str(job_id) if job_id else None
        self._selected_state = str(state) if state else None
        self._sync_action_buttons()

        if self._selected_job_id and not self._busy():
            set_pathena_ui_state(self.details, "busy")
            self._start(
                "show",
                ["show", self._selected_job_id],
                "Loading durable job details",
            )

    def _refresh_if_visible(self) -> None:
        if self.isVisible() and not self._busy():
            self.refresh()

    def _refresh_scheduler_status(self) -> None:
        supervisor = self._scheduler_supervisor
        if supervisor is None:
            self.scheduler_status.setText("SCHEDULER · EXTERNAL")
            set_pathena_ui_state(self.scheduler_status, "idle")
            return
        if supervisor.stopping:
            self.scheduler_status.setText("SCHEDULER · STOPPING")
            set_pathena_ui_state(self.scheduler_status, "busy")
        elif supervisor.child_active:
            self.scheduler_status.setText("SCHEDULER · ACTIVE")
            set_pathena_ui_state(self.scheduler_status, "success")
        else:
            self.scheduler_status.setText("SCHEDULER · RECOVERY PENDING")
            set_pathena_ui_state(self.scheduler_status, "busy")

    def _busy(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning

    def _start(self, operation: str, arguments: list[str], label: str) -> None:
        self._operation = operation
        self._buffer = ""
        self.status.setText(label + " …")
        set_pathena_ui_state(self.status, "busy")
        self._sync_action_buttons(force_disabled=True)
        self._process.start(sys.executable, ["-m", "athena.desktop.jobs_cli", *arguments])

    def _sync_action_buttons(self, *, force_disabled: bool = False) -> None:
        if force_disabled or self._busy():
            self.refresh_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
            self.wake_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            return

        state = self._selected_state
        self.refresh_button.setEnabled(True)
        self.pause_button.setEnabled(state in _PAUSABLE_STATES)
        self.resume_button.setEnabled(state in _RESUMABLE_STATES)
        self.wake_button.setEnabled(state in _WAKEABLE_STATES)
        self.cancel_button.setEnabled(
            state is not None
            and state not in _TERMINAL_STATES
            and state != "cancel_requested"
        )

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation != "list":
            self.details.moveCursor(QTextCursor.MoveOperation.End)
            self.details.insertPlainText(chunk)

    def _process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._drain_output()
        operation = self._operation
        output = self._buffer
        self._operation = ""
        self._sync_action_buttons()

        if exit_code != 0:
            self.status.setText(f"Jobs command failed (exit {exit_code}).")
            set_pathena_ui_state(self.status, "error")
            set_pathena_ui_state(self.details, "error")
            if operation == "list":
                self.details.setPlainText(output)
            return

        if operation == "list":
            self._render_job_list(output)
            self.status.setText(f"Durable jobs refreshed: {self.jobs.count()} shown.")
            set_pathena_ui_state(self.status, "success")
            return

        if operation == "show":
            self.status.setText("Durable job details loaded.")
            set_pathena_ui_state(self.status, "success")
            set_pathena_ui_state(self.details, "success")
            return

        self.status.setText(f"{operation.upper()} transition persisted.")
        set_pathena_ui_state(self.status, "success")
        set_pathena_ui_state(self.details, "success")
        QTimer.singleShot(120, self.refresh)

    def _render_job_list(self, output: str) -> None:
        selected = self._selected_job_id
        self.jobs.blockSignals(True)
        self.jobs.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 7)
            if len(parts) != 8:
                continue
            job_id, state, priority, job_type, stage, retries, _updated_at_us, summary = parts
            item = QListWidgetItem(
                f"{state.upper():<18} P{priority}  {job_type:<24}  {stage:<18}  {summary}"
            )
            item.setToolTip(f"{job_id}\nstate={state}\nstage={stage}\nretries={retries}")
            item.setData(Qt.ItemDataRole.UserRole, job_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, state)
            self.jobs.addItem(item)
            if selected == job_id:
                item_to_select = item

        self.jobs.blockSignals(False)

        if item_to_select is not None:
            set_pathena_ui_state(self.jobs, "success")
            self.jobs.setCurrentItem(item_to_select)
            self._selection_changed(item_to_select, None)
        elif self.jobs.count() > 0:
            set_pathena_ui_state(self.jobs, "success")
            self.jobs.setCurrentRow(0)
        else:
            self._selected_job_id = None
            self._selected_state = None
            self._sync_action_buttons()
            self.details.setPlainText(
                "No durable jobs have been persisted yet. Research and Source operations "
                "will appear here as soon as they are queued."
            )
            set_pathena_ui_state(self.jobs, "empty")
            set_pathena_ui_state(self.details, "empty")

    def _process_error(self, error: QProcess.ProcessError) -> None:
        self._operation = ""
        self._sync_action_buttons()
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText("Unable to start the local pATHENA jobs command.")
        else:
            self.status.setText(f"Jobs command error: {error.name}")
        set_pathena_ui_state(self.status, "error")
        set_pathena_ui_state(self.details, "error")


def install_jobs_workspace(
    window: object,
    scheduler_supervisor: DesktopJobSchedulerSupervisor | None = None,
) -> JobsWorkspace:
    """Replace the JOBS shell placeholder without widening window.py."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 3:
        raise RuntimeError("pATHENA desktop JOBS page is unavailable")

    placeholder = pages.widget(3)
    workspace = JobsWorkspace(scheduler_supervisor=scheduler_supervisor)
    pages.removeWidget(placeholder)
    pages.insertWidget(3, workspace)
    placeholder.deleteLater()
    return workspace
