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

from athena.desktop.jobs_lifecycle import (
    JobLifecycleError,
    JobListEntry,
    action_availability,
    parse_job_list,
    parse_current_progress,
    parse_transition_receipt,
)
from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state
from athena.desktop.scheduler_supervisor import DesktopJobSchedulerSupervisor


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
        self._operation_job_id: str | None = None
        self._buffer = ""
        self._selected_job_id: str | None = None
        self._selected_state: str | None = None
        self._process_error_reported = False

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
        self.status.setAccessibleDescription(self.status.text())
        set_pathena_ui_state(self.status, "idle")

        self.progress = QLabel("PROGRESS · Select a job.")
        self.progress.setObjectName("jobProgress")
        self.progress.setAccessibleName("Job progress")
        set_pathena_ui_state(self.progress, "empty")

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
            "Select a job to inspect its current state and activity."
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
        title = QLabel("JOBS")
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
            "Background work from Research and Sources appears here. Select a job to "
            "inspect its state and activity, or use the available controls to manage it."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.jobs)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self._refresh_scheduler_status()
        self._sync_action_buttons()
        QTimer.singleShot(0, self.refresh)

    @staticmethod
    def _job_label(job_id: str | None) -> str:
        return job_id[:8].upper() if job_id else ""

    def _set_status(
        self,
        text: str,
        state: str,
        *,
        diagnostic: str = "",
    ) -> None:
        self.status.setText(text)
        self.status.setToolTip(diagnostic)
        description = text if not diagnostic else f"{text} {diagnostic}"
        self.status.setAccessibleDescription(description)
        set_pathena_ui_state(self.status, state)

    def refresh(self) -> None:
        if self._busy():
            return
        self._start("list", ["list", "--limit", "150"], "Refreshing jobs")

    def pause_selected(self) -> None:
        self._transition("pause", "Pausing selected job")

    def resume_selected(self) -> None:
        self._transition("resume", "Resuming selected job")

    def wake_selected(self) -> None:
        self._transition("wake", "Waking selected job")

    def cancel_selected(self) -> None:
        self._transition("cancel", "Requesting cancellation")

    def _transition(self, operation: str, label: str) -> None:
        job_id = self._selected_job_id
        if self._busy() or not job_id:
            return
        set_pathena_ui_state(self.details, "busy")
        self._start(operation, [operation, job_id], label, job_id=job_id)

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

        if self._busy():
            if current is not None and not self._operation_owns_details():
                owner_label = self._job_label(self._operation_job_id)
                selected_label = self._job_label(self._selected_job_id)
                self.details.setPlainText(
                    f"BACKGROUND · {self._operation.upper()} for job {owner_label} is still "
                    "running.\n"
                    f"CURRENT · Job {selected_label} remains selected; background output "
                    "will not be written into this pane.\n\n"
                    f"{current.toolTip()}"
                )
                self.details.setProperty(
                    "pathenaBackgroundOperationOwner",
                    self._operation_job_id or "",
                )
                set_pathena_ui_state(self.details, "idle")
            return

        self.details.setProperty("pathenaBackgroundOperationOwner", "")
        if self._selected_job_id:
            selected_job_id = self._selected_job_id
            set_pathena_ui_state(self.details, "busy")
            self.progress.setText("PROGRESS · Loading durable checkpoint state …")
            set_pathena_ui_state(self.progress, "busy")
            self._start(
                "show",
                ["show", selected_job_id],
                "Loading job details",
                job_id=selected_job_id,
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

    def _start(
        self,
        operation: str,
        arguments: list[str],
        label: str,
        *,
        job_id: str | None = None,
    ) -> None:
        self._operation = operation
        self._operation_job_id = job_id
        self._buffer = ""
        self._process_error_reported = False
        job_label = self._job_label(job_id)
        if job_label and operation != "list":
            label = f"{label} · {job_label}"
        self._set_status(label + " …", "busy")
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
        availability = action_availability(state)
        self.refresh_button.setEnabled(True)
        for action, button in (
            ("pause", self.pause_button),
            ("resume", self.resume_button),
            ("wake", self.wake_button),
            ("cancel", self.cancel_button),
        ):
            button.setEnabled(bool(getattr(availability, action)))
            reason = availability.reason(action)
            button.setToolTip(reason)
            button.setAccessibleDescription(reason)

    def _operation_owns_details(self) -> bool:
        return self._operation_job_id == self._selected_job_id

    def _reload_selected_details_if_idle(self) -> None:
        if self._busy() or not self._selected_job_id:
            return
        current = self.jobs.currentItem()
        if (
            current is None
            or current.data(Qt.ItemDataRole.UserRole) != self._selected_job_id
        ):
            return
        self.details.setProperty("pathenaBackgroundOperationOwner", "")
        set_pathena_ui_state(self.details, "busy")
        selected_job_id = self._selected_job_id
        self._start(
            "show",
            ["show", selected_job_id],
            "Loading job details",
            job_id=selected_job_id,
        )

    def _recover_background_selection(
        self,
        operation: str,
        *,
        owns_details: bool,
    ) -> None:
        if operation == "list" or owns_details or not self._selected_job_id:
            return
        QTimer.singleShot(0, self._reload_selected_details_if_idle)

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8",
            errors="replace",
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation == "show" and self._operation_owns_details():
            self.details.moveCursor(QTextCursor.MoveOperation.End)
            self.details.insertPlainText(chunk)

    def _process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._drain_output()
        if self._process_error_reported:
            self._process_error_reported = False
            self._operation = ""
            self._operation_job_id = None
            self._sync_action_buttons()
            if self.details.property("pathenaBackgroundOperationOwner"):
                QTimer.singleShot(0, self._reload_selected_details_if_idle)
            return

        operation = self._operation
        operation_job_id = self._operation_job_id
        owns_details = self._operation_owns_details()
        output = self._buffer
        self._operation = ""
        self._operation_job_id = None
        self._sync_action_buttons()
        job_label = self._job_label(operation_job_id)

        if exit_code != 0:
            if operation == "list":
                message = f"Jobs could not be refreshed (exit {exit_code})."
            elif operation == "show" and job_label:
                message = f"Job {job_label} details could not be loaded (exit {exit_code})."
            else:
                action = operation.upper() if operation else "JOB ACTION"
                subject = f" for job {job_label}" if job_label else ""
                location = " in the background" if subject and not owns_details else ""
                message = f"{action} failed{subject}{location} (exit {exit_code})."
            self._set_status(message, "error")
            if owns_details:
                set_pathena_ui_state(self.details, "error")
            if operation == "list" and self._selected_job_id is None:
                self.details.setPlainText(output)
                set_pathena_ui_state(self.details, "error")
            self._recover_background_selection(
                operation,
                owns_details=owns_details,
            )
            return

        if operation == "list":
            try:
                rows = parse_job_list(output)
            except JobLifecycleError as exc:
                self._set_status(
                    "Jobs could not be refreshed because the local response was invalid.",
                    "error",
                    diagnostic=str(exc),
                )
                if self._selected_job_id is None:
                    self.details.setPlainText(
                        "JOBS REFRESH COULD NOT BE VERIFIED\n"
                        f"{exc}\n\nDiagnostic details:\n{output}"
                    )
                    set_pathena_ui_state(self.details, "error")
                return
            self._render_job_list(rows)
            self._set_status(
                f"Jobs refreshed: {self.jobs.count()} shown.",
                "success",
            )
            return

        if operation == "show":
            self._set_status(f"Job {job_label} details loaded.", "success")
            if owns_details:
                set_pathena_ui_state(self.details, "success")
                progress = parse_current_progress(output)
                if progress is None:
                    self.progress.setText("PROGRESS · No durable checkpoint progress recorded.")
                    set_pathena_ui_state(self.progress, "idle")
                else:
                    self.progress.setText(f"PROGRESS · {progress}")
                    self.progress.setToolTip(progress)
                    set_pathena_ui_state(self.progress, "success")
            self._recover_background_selection(
                operation,
                owns_details=owns_details,
            )
            return

        try:
            receipt = parse_transition_receipt(
                output,
                expected_operation=operation,
                expected_job_id=operation_job_id or "",
            )
        except JobLifecycleError as exc:
            self._set_status(
                f"{operation.upper()} response for job {job_label} could not be verified.",
                "error",
                diagnostic=str(exc),
            )
            if owns_details:
                self.details.setPlainText(
                    f"JOB ACTION COULD NOT BE VERIFIED\n{exc}\n\nDiagnostic details:\n{output}"
                )
                set_pathena_ui_state(self.details, "error")
            self._recover_background_selection(
                operation,
                owns_details=owns_details,
            )
            return

        if owns_details:
            self._selected_state = receipt.state
            current = self.jobs.currentItem()
            if current is not None and current.data(Qt.ItemDataRole.UserRole) == receipt.job_id:
                current.setData(Qt.ItemDataRole.UserRole + 1, receipt.state)
        self._sync_action_buttons()
        self._set_status(
            f"{operation.upper()} completed for job {job_label} · "
            f"{receipt.state.upper()}.",
            "success",
        )
        if owns_details:
            detail_message = (
                f"JOB UPDATED · {operation.upper()} completed · "
                f"{receipt.state.upper()}. Refreshing current details…"
            )
            self.details.setPlainText(detail_message)
            self.details.setAccessibleDescription(detail_message)
            set_pathena_ui_state(self.details, "busy")
        self._recover_background_selection(
            operation,
            owns_details=owns_details,
        )
        QTimer.singleShot(120, self.refresh)

    def _render_job_list(self, rows: tuple[JobListEntry, ...]) -> None:
        selected = self._selected_job_id
        self.jobs.blockSignals(True)
        self.jobs.clear()
        item_to_select: QListWidgetItem | None = None

        for row in rows:
            job_id = row.job_id
            state = row.state
            priority = row.priority
            job_type = row.job_type
            stage = row.stage
            retries = row.retries
            summary = row.summary
            item = QListWidgetItem(
                f"{state.upper():<18} P{priority}  {job_type:<24}  {stage:<18}  {summary}"
            )
            item.setToolTip(f"{job_id}\nstate={state}\nstage={stage}\nretries={retries}")
            item.setData(Qt.ItemDataRole.UserRole, job_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, state)
            item.setData(Qt.ItemDataRole.UserRole + 2, stage)
            self.jobs.addItem(item)
            if selected == job_id:
                item_to_select = item

        self.jobs.blockSignals(False)
        self.jobs.setProperty("pathenaSelectionDisappeared", "")
        self.details.setProperty("pathenaSelectionDisappeared", "")

        if item_to_select is not None:
            set_pathena_ui_state(self.jobs, "success")
            self.jobs.setCurrentItem(item_to_select)
            self._selection_changed(item_to_select, None)
        elif self.jobs.count() > 0 and selected is not None:
            set_pathena_ui_state(self.jobs, "success")
            self._selected_job_id = None
            self._selected_state = None
            self._sync_action_buttons()
            self.jobs.setCurrentRow(-1)
            job_label = self._job_label(selected)
            message = (
                f"SELECTION CHANGED · Job {job_label} is no longer listed after refresh. "
                "Select another job to inspect its current state."
            )
            self.details.setPlainText(message)
            self.jobs.setProperty("pathenaSelectionDisappeared", selected)
            self.details.setProperty("pathenaSelectionDisappeared", selected)
            self.details.setAccessibleDescription(message)
            self.jobs.setStatusTip(message)
            set_pathena_ui_state(self.details, "empty")
        elif self.jobs.count() > 0:
            set_pathena_ui_state(self.jobs, "success")
            self.jobs.setCurrentRow(0)
        else:
            self._selected_job_id = None
            self._selected_state = None
            self._sync_action_buttons()
            self.details.setPlainText(
                "No jobs are available yet. Research and Source operations will appear "
                "here when they are queued."
            )
            set_pathena_ui_state(self.jobs, "empty")
            set_pathena_ui_state(self.details, "empty")

    def _process_error(self, error: QProcess.ProcessError) -> None:
        self._process_error_reported = True
        job_id = self._operation_job_id
        owns_details = self._operation_owns_details()
        operation = self._operation
        self._operation = ""
        self._operation_job_id = None
        self._sync_action_buttons()
        job_label = self._job_label(job_id)
        subject = f" for job {job_label}" if job_label else ""
        if operation == "list":
            label = "Jobs refresh"
        elif operation == "show":
            label = "Job details"
        elif operation:
            label = operation.upper()
        else:
            label = "Jobs operation"
        if error == QProcess.ProcessError.FailedToStart:
            message = f"{label}{subject} could not be started."
        else:
            message = f"{label}{subject} failed: {error.name}"
        self._set_status(message, "error")
        if owns_details:
            set_pathena_ui_state(self.details, "error")
        self._recover_background_selection(
            operation,
            owns_details=owns_details,
        )


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
