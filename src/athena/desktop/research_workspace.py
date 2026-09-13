"""Functional RESEARCH workspace for the native pATHENA desktop shell."""

from __future__ import annotations

import re
import sys

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state
from athena.desktop.workspace_detail_presenter import format_research_show

_JOB_QUEUED_RE = re.compile(r"^JOB_QUEUED\s+([0-9a-fA-F-]{36})$", re.MULTILINE)
_TERMINAL_STATES = frozenset({"cancelled", "failed", "completed"})


def _operation_owns_selected_job(
    operation_job_id: str | None,
    selected_job_id: str | None,
) -> bool:
    """Return whether job-scoped async output still belongs to the visible selection."""
    return operation_job_id is not None and operation_job_id == selected_job_id


class ResearchWorkspace(QWidget):
    """Queue, inspect and cancel durable exhaustive research without blocking Qt."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("researchWorkspace")
        self._operation = ""
        self._operation_job_id: str | None = None
        self._buffer = ""
        self._selected_job_id: str | None = None
        self._selected_job_state: str | None = None

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Research question across local Sources…")
        self.query_input.returnPressed.connect(self.enqueue)

        self.start_button = QPushButton("START RESEARCH")
        self.start_button.setObjectName("newChatButton")
        self.start_button.clicked.connect(self.enqueue)

        self.refresh_button = QPushButton("REFRESH")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.clicked.connect(self.refresh)

        self.cancel_button = QPushButton("CANCEL SELECTED")
        self.cancel_button.setObjectName("newChatButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_selected)

        self.status = QLabel("Ready.")
        self.status.setObjectName("researchStatus")
        self.status.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        set_pathena_ui_state(self.status, "idle")

        self.jobs = QListWidget()
        self.jobs.setObjectName("researchJobList")
        self.jobs.setMinimumWidth(320)
        self.jobs.currentItemChanged.connect(self._selection_changed)
        set_pathena_ui_state(self.jobs, "idle")

        self.details = QPlainTextEdit()
        self.details.setObjectName("researchDetails")
        self.details.setReadOnly(True)
        self.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.details.setPlaceholderText(
            "Select a research job to inspect scope, coverage and work items."
        )
        set_pathena_ui_state(self.details, "empty")

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._drain_output)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("EXHAUSTIVE LOCAL RESEARCH")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.refresh_button)
        header.addWidget(self.cancel_button)
        layout.addLayout(header)

        intro = QLabel(
            "Durable research runs against pATHENA's frozen local Source snapshot. "
            "Jobs survive restarts and are executed by the existing scheduler; this "
            "workspace only controls and observes the canonical research pipeline."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        composer = QHBoxLayout()
        composer.addWidget(self.query_input, 1)
        composer.addWidget(self.start_button)
        layout.addLayout(composer)
        layout.addWidget(self.status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.jobs)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        QTimer.singleShot(0, self.refresh)

    @staticmethod
    def _job_label(job_id: str | None) -> str:
        return job_id[:8].upper() if job_id else ""

    def enqueue(self) -> None:
        query = self.query_input.text().strip()
        if not query or self._busy():
            return
        self.details.clear()
        set_pathena_ui_state(self.details, "busy")
        self._start("enqueue", ["enqueue", query], "Queueing durable research")

    def refresh(self) -> None:
        if self._busy():
            return
        self._start("list", ["list", "--limit", "100"], "Refreshing research jobs")

    def cancel_selected(self) -> None:
        if self._busy() or not self._cancel_available():
            return
        assert self._selected_job_id is not None
        job_id = self._selected_job_id
        self._start(
            "cancel",
            ["cancel", job_id],
            "Requesting research cancellation",
            job_id=job_id,
        )

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        job_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        state = None if current is None else current.data(Qt.ItemDataRole.UserRole + 1)
        self._selected_job_id = str(job_id) if job_id else None
        self._selected_job_state = str(state) if state else None
        self._sync_cancel_button()

        if self._busy():
            if current is not None and not self._operation_owns_details():
                owner_label = self._job_label(self._operation_job_id)
                selected_label = self._job_label(self._selected_job_id)
                if self._operation_job_id is None:
                    background = f"{self._operation.upper()} is still running."
                    owner = self._operation or "background"
                else:
                    background = (
                        f"{self._operation.upper()} for research run {owner_label} is still "
                        "running in the background."
                    )
                    owner = self._operation_job_id
                self.details.setPlainText(
                    f"BACKGROUND · {background}\n"
                    f"CURRENT · Research run {selected_label} remains selected; background "
                    "output will not be written into this pane.\n\n"
                    f"{current.toolTip()}"
                )
                self.details.setProperty("pathenaBackgroundOperationOwner", owner)
                set_pathena_ui_state(self.details, "idle")
            return

        self.details.setProperty("pathenaBackgroundOperationOwner", "")
        if self._selected_job_id:
            selected_job_id = self._selected_job_id
            self.details.clear()
            set_pathena_ui_state(self.details, "busy")
            self._start(
                "show",
                ["show", selected_job_id],
                "Loading research details",
                job_id=selected_job_id,
            )

    def _busy(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning

    def _operation_owns_details(self) -> bool:
        return _operation_owns_selected_job(
            self._operation_job_id,
            self._selected_job_id,
        )

    def _cancel_available(self) -> bool:
        return (
            bool(self._selected_job_id)
            and self._selected_job_state is not None
            and self._selected_job_state not in _TERMINAL_STATES
            and self._selected_job_state != "cancel_requested"
        )

    def _sync_cancel_button(self) -> None:
        enabled = not self._busy() and self._cancel_available()
        self.cancel_button.setEnabled(enabled)
        job_label = self._job_label(self._selected_job_id) or "none"
        state = self._selected_job_state or "none"
        if enabled:
            reason = f"Request cancellation for research run {job_label} ({state})."
        elif self._selected_job_id is None:
            reason = "Select a research run before requesting cancellation."
        elif state == "cancel_requested":
            reason = f"Research run {job_label} already has cancellation requested."
        elif state in _TERMINAL_STATES:
            reason = f"Research run {job_label} is already terminal ({state})."
        else:
            reason = f"Research run {job_label} cannot be cancelled in state {state}."
        self.cancel_button.setToolTip(reason)
        self.cancel_button.setAccessibleDescription(reason)
        self.cancel_button.setProperty("pathenaResearchJobState", state)
        self.cancel_button.setProperty("pathenaResearchCancelAvailable", enabled)

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
        job_label = self._job_label(job_id)
        if job_label:
            label = f"{label} · {job_label}"
        self.status.setText(label + " …")
        set_pathena_ui_state(self.status, "busy")
        self._set_controls_enabled(False)
        self._process.start(
            sys.executable,
            ["-m", "athena.desktop.research_cli", *arguments],
        )

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.query_input.setEnabled(enabled)
        self.start_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        if enabled:
            self._sync_cancel_button()
        else:
            self.cancel_button.setEnabled(False)

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation == "cancel" and self._operation_owns_details():
            self.details.appendPlainText(chunk.rstrip("\n"))

    def _process_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._drain_output()
        operation = self._operation
        operation_job_id = self._operation_job_id
        owns_details = self._operation_owns_details()
        output = self._buffer
        self._operation = ""
        self._operation_job_id = None
        self._set_controls_enabled(True)
        job_label = self._job_label(operation_job_id)

        if exit_code != 0:
            subject = f" for research run {job_label}" if job_label else ""
            location = " in the background" if subject and not owns_details else ""
            self.status.setText(
                f"Research command{subject} failed{location} (exit {exit_code})."
            )
            set_pathena_ui_state(self.status, "error")
            if operation == "list":
                self.details.setPlainText(output)
                set_pathena_ui_state(self.details, "error")
            elif owns_details:
                if operation == "show":
                    self.details.setPlainText(output)
                set_pathena_ui_state(self.details, "error")
            return

        if operation == "list":
            self._render_job_list(output)
            self.status.setText(f"Research jobs refreshed: {self.jobs.count()} shown.")
            set_pathena_ui_state(self.status, "success")
            return

        if operation == "enqueue":
            match = _JOB_QUEUED_RE.search(output)
            if match is not None:
                self._selected_job_id = match.group(1)
                self._selected_job_state = "queued"
            self.query_input.clear()
            self.status.setText("Research job queued.")
            set_pathena_ui_state(self.status, "success")
            set_pathena_ui_state(self.details, "success")
            QTimer.singleShot(120, self.refresh)
            return

        if operation == "cancel":
            if owns_details:
                self._selected_job_state = "cancel_requested"
                self._sync_cancel_button()
                set_pathena_ui_state(self.details, "success")
            subject = f" for research run {job_label}" if job_label else ""
            location = " in the background" if subject and not owns_details else ""
            self.status.setText(f"Cancellation request persisted{subject}{location}.")
            set_pathena_ui_state(self.status, "success")
            QTimer.singleShot(120, self.refresh)
            return

        if operation == "show":
            subject = f"Research run {job_label}" if job_label else "Research"
            if owns_details:
                self.details.setPlainText(format_research_show(output))
                self.details.setProperty("pathenaBackgroundOperationOwner", "")
                set_pathena_ui_state(self.details, "success")
                self.status.setText(f"{subject} details loaded.")
            else:
                self.status.setText(
                    f"{subject} details loaded in the background; selection changed."
                )
            set_pathena_ui_state(self.status, "success")

    def _render_job_list(self, output: str) -> None:
        selected = self._selected_job_id
        self.jobs.blockSignals(True)
        self.jobs.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 4)
            if len(parts) != 5:
                continue
            job_id, state, stage, coverage, query = parts
            coverage_label = "—" if coverage == "-" else f"{float(coverage) * 100:.1f}%"
            item = QListWidgetItem(
                f"{state.upper():<16} {coverage_label:>7}  {query or '<no query>'}"
            )
            item.setToolTip(
                f"{job_id}\nstate={state}\nstage={stage}\ncoverage={coverage_label}"
            )
            item.setData(Qt.ItemDataRole.UserRole, job_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, state)
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
            self._selected_job_state = None
            self._sync_cancel_button()
            self.jobs.setCurrentRow(-1)
            job_label = selected[:8].upper()
            message = (
                f"SELECTION CHANGED · Research run {job_label} is no longer listed after "
                "refresh. Select another research run to inspect its current state."
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
            self._selected_job_state = None
            self._sync_cancel_button()
            self.details.setPlainText(
                "No exhaustive research jobs yet. Enter a question above to create one."
            )
            set_pathena_ui_state(self.jobs, "empty")
            set_pathena_ui_state(self.details, "empty")

    def _process_error(self, error: QProcess.ProcessError) -> None:
        operation = self._operation
        operation_job_id = self._operation_job_id
        owns_details = self._operation_owns_details()
        self._operation = ""
        self._operation_job_id = None
        self._set_controls_enabled(True)
        job_label = self._job_label(operation_job_id)
        subject = f" for research run {job_label}" if job_label else ""
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText(f"Unable to start the local pATHENA research command{subject}.")
        else:
            self.status.setText(f"Research command{subject} error: {error.name}")
        set_pathena_ui_state(self.status, "error")
        if operation == "list" or owns_details:
            set_pathena_ui_state(self.details, "error")


def install_research_workspace(window: object) -> ResearchWorkspace:
    """Replace the RESEARCH shell placeholder without widening window.py."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 2:
        raise RuntimeError("pATHENA desktop RESEARCH page is unavailable")

    placeholder = pages.widget(2)
    workspace = ResearchWorkspace()
    pages.removeWidget(placeholder)
    pages.insertWidget(2, workspace)
    placeholder.deleteLater()
    return workspace
