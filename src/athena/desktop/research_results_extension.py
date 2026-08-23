"""Progressive ResearchResult and promotion controls for the pATHENA desktop."""

from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QProcess, Qt, QTimer, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.research_workspace import ResearchWorkspace


class ResearchResultsExtension(QObject):
    """Expose immutable results and explicit Research promotion beside durable jobs."""

    def __init__(self, workspace: ResearchWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._operation = ""
        self._operation_job_id: str | None = None
        self._buffer = ""
        self._selected_proposal_id: str | None = None

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._drain_output)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._process_error)

        self._install_job_filter()
        self._install_result_panel()
        workspace.jobs.currentItemChanged.connect(self._job_selection_changed)
        workspace._process.finished.connect(self._base_process_finished)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(10_000)
        self.refresh_timer.timeout.connect(self._periodic_refresh)
        self.refresh_timer.start()
        self._sync_job_actions()

    def _install_job_filter(self) -> None:
        self.job_filter = QLineEdit()
        self.job_filter.setObjectName("researchJobFilter")
        self.job_filter.setPlaceholderText("Filter research runs…")
        self.job_filter.setClearButtonEnabled(True)
        self.job_filter.textChanged.connect(self._apply_job_filter)

        root = self.workspace.layout()
        if isinstance(root, QVBoxLayout):
            index = root.indexOf(self.workspace.status)
            root.insertWidget(index + 1, self.job_filter)

    def _install_result_panel(self) -> None:
        self.result_button = QPushButton("LOAD RESULT")
        self.propose_button = QPushButton("CREATE PROPOSALS")
        self.refresh_proposals_button = QPushButton("PROPOSALS")
        for button in (
            self.result_button,
            self.propose_button,
            self.refresh_proposals_button,
        ):
            button.setObjectName("newChatButton")
            button.setEnabled(False)

        self.result_button.clicked.connect(self.load_result)
        self.propose_button.clicked.connect(self.create_proposals)
        self.refresh_proposals_button.clicked.connect(self.load_proposals)

        self.proposal_status = QLabel("Select a completed Research run to inspect its result.")
        self.proposal_status.setObjectName("settingsHelp")
        self.proposal_list = QListWidget()
        self.proposal_list.setObjectName("researchProposalList")
        self.proposal_list.setMaximumHeight(190)
        self.proposal_list.currentItemChanged.connect(self._proposal_selection_changed)

        self.accept_button = QPushButton("ACCEPT")
        self.accept_separate_button = QPushButton("ACCEPT AS SEPARATE")
        self.reject_button = QPushButton("REJECT")
        for button in (self.accept_button, self.accept_separate_button, self.reject_button):
            button.setObjectName("newChatButton")
            button.setEnabled(False)
        self.accept_button.setToolTip(
            "Accept the selected evidence-backed Research proposal into canonical memory"
        )
        self.accept_separate_button.setToolTip(
            "Explicitly keep a surfaced near-duplicate separate while accepting"
        )
        self.reject_button.setToolTip(
            "Reject or acknowledge the selected Research proposal without canonicalizing it"
        )
        self.accept_button.clicked.connect(lambda: self.accept_selected(False))
        self.accept_separate_button.clicked.connect(lambda: self.accept_selected(True))
        self.reject_button.clicked.connect(self.reject_selected)

        splitter = self.workspace.details.parentWidget()
        if not isinstance(splitter, QSplitter):
            return
        old_index = splitter.indexOf(self.workspace.details)
        container = QWidget()
        container.setObjectName("researchResultPanel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        heading = QLabel("RESULT / PROMOTION")
        heading.setProperty("role", "section")
        controls.addWidget(heading)
        controls.addStretch(1)
        controls.addWidget(self.result_button)
        controls.addWidget(self.propose_button)
        controls.addWidget(self.refresh_proposals_button)
        layout.addLayout(controls)
        layout.addWidget(self.workspace.details, 2)
        layout.addWidget(self.proposal_status)
        layout.addWidget(self.proposal_list, 1)

        decision_row = QHBoxLayout()
        decision_row.addStretch(1)
        decision_row.addWidget(self.reject_button)
        decision_row.addWidget(self.accept_separate_button)
        decision_row.addWidget(self.accept_button)
        layout.addLayout(decision_row)
        splitter.insertWidget(max(0, old_index), container)

    def _busy(self) -> bool:
        return self.process.state() != QProcess.ProcessState.NotRunning

    def _selected_job_id(self) -> str | None:
        return self.workspace._selected_job_id

    def _selected_job_state(self) -> str:
        row = self.workspace.jobs.currentRow()
        if row < 0:
            return ""
        text = self.workspace.jobs.item(row).text().strip()
        return text.split(None, 1)[0].casefold() if text else ""

    def _job_selection_changed(
        self,
        _current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self._selected_proposal_id = None
        self.proposal_list.clear()
        if self._busy() and self._operation_job_id != self._selected_job_id():
            self.proposal_status.setText(
                "Another Research run is still completing its result operation. "
                "This selection will not receive that run's output."
            )
        else:
            self.proposal_status.setText(
                "Load proposals for the selected completed Research run."
            )
        self._sync_job_actions()

    def _sync_job_actions(self) -> None:
        has_job = bool(self._selected_job_id())
        terminal_success = self._selected_job_state() == "completed"
        enabled = has_job and terminal_success and not self._busy()
        self.result_button.setEnabled(enabled)
        self.propose_button.setEnabled(enabled)
        self.refresh_proposals_button.setEnabled(enabled)

        terminal = self._selected_job_state() in {"completed", "failed", "cancelled"}
        if terminal:
            self.workspace.cancel_button.setEnabled(False)

        self._sync_proposal_actions()

    def _sync_proposal_actions(self) -> None:
        row = self.proposal_list.currentRow()
        if row < 0:
            pending = False
            proposal_type = ""
        else:
            item = self.proposal_list.item(row)
            pending = item.data(Qt.ItemDataRole.UserRole + 1) == "pending"
            proposal_type = str(item.data(Qt.ItemDataRole.UserRole + 2) or "")
        enabled = pending and not self._busy()
        can_accept = enabled and proposal_type != "contradiction"
        self.accept_button.setEnabled(can_accept)
        self.accept_separate_button.setEnabled(can_accept)
        self.reject_button.setEnabled(enabled)

    @Slot()
    def load_result(self) -> None:
        job_id = self._selected_job_id()
        if job_id:
            self._start("result", ["result", job_id], clear_details=True, job_id=job_id)

    @Slot()
    def create_proposals(self) -> None:
        job_id = self._selected_job_id()
        if job_id:
            self._start("propose", ["propose", job_id], job_id=job_id)

    @Slot()
    def load_proposals(self) -> None:
        job_id = self._selected_job_id()
        if job_id:
            self._start("proposals", ["proposals", job_id], job_id=job_id)

    def accept_selected(self, keep_separate: bool) -> None:
        proposal_id = self._selected_proposal_id
        if not proposal_id:
            return
        arguments = ["accept", proposal_id]
        if keep_separate:
            arguments.append("--keep-separate-near-duplicates")
        self._start("accept", arguments, job_id=self._selected_job_id())

    @Slot()
    def reject_selected(self) -> None:
        proposal_id = self._selected_proposal_id
        if proposal_id:
            self._start("reject", ["reject", proposal_id], job_id=self._selected_job_id())

    def _start(
        self,
        operation: str,
        arguments: list[str],
        *,
        clear_details: bool = False,
        job_id: str | None = None,
    ) -> None:
        if self._busy():
            return
        self._operation = operation
        self._operation_job_id = job_id
        self._buffer = ""
        if clear_details:
            self.workspace.details.clear()
        self._set_extension_controls(False)
        self.proposal_status.setText(
            {
                "result": "Loading immutable ResearchResult and evidence …",
                "propose": "Freezing deterministic Research proposals …",
                "proposals": "Loading frozen Research proposals …",
                "accept": "Accepting selected Research proposal …",
                "reject": "Rejecting selected Research proposal …",
            }.get(operation, "Updating Research result …")
        )
        self.process.start(
            sys.executable,
            ["-m", "athena.desktop.research_results_cli", *arguments],
        )

    def _set_extension_controls(self, enabled: bool) -> None:
        if not enabled:
            for button in (
                self.result_button,
                self.propose_button,
                self.refresh_proposals_button,
                self.accept_button,
                self.accept_separate_button,
                self.reject_button,
            ):
                button.setEnabled(False)
            return
        self._sync_job_actions()

    def _operation_owns_selection(self) -> bool:
        job_id = self._operation_job_id
        return job_id is None or job_id == self._selected_job_id()

    @Slot()
    def _drain_output(self) -> None:
        chunk = bytes(self.process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation == "result" and self._operation_owns_selection():
            self.workspace.details.insertPlainText(chunk)

    @Slot(int, QProcess.ExitStatus)
    def _finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._drain_output()
        operation = self._operation
        operation_job_id = self._operation_job_id
        output = self._buffer
        owns_selection = self._operation_owns_selection()
        self._operation = ""
        self._operation_job_id = None
        self._set_extension_controls(True)

        if not owns_selection:
            self.proposal_status.setText(
                "The previous Research run finished in the background. "
                "Load result or proposals for the currently selected run."
            )
            return

        if exit_code != 0:
            self.proposal_status.setText(f"Research result command failed (exit {exit_code}).")
            if output and operation != "result":
                self.workspace.details.setPlainText(output)
            return

        if operation == "result":
            self.proposal_status.setText("Immutable ResearchResult and evidence loaded.")
        elif operation in {"propose", "proposals"}:
            self._render_proposals(output)
            verb = "created" if operation == "propose" else "loaded"
            self.proposal_status.setText(
                f"Research proposals {verb}: {self.proposal_list.count()} shown."
            )
        elif operation == "accept":
            self.proposal_status.setText("Research proposal accepted into canonical memory.")
            if operation_job_id == self._selected_job_id():
                QTimer.singleShot(120, self.load_proposals)
        elif operation == "reject":
            self.proposal_status.setText("Research proposal rejected/acknowledged.")
            if operation_job_id == self._selected_job_id():
                QTimer.singleShot(120, self.load_proposals)

    def _render_proposals(self, output: str) -> None:
        selected = self._selected_proposal_id
        self.proposal_list.blockSignals(True)
        self.proposal_list.clear()
        selected_item: QListWidgetItem | None = None
        for raw_line in output.splitlines():
            if not raw_line.startswith("PROPOSAL\t"):
                continue
            parts = raw_line.split("\t", 8)
            if len(parts) != 9:
                continue
            (
                _,
                proposal_id,
                ordinal,
                proposal_type,
                state,
                evidence_kind,
                evidence_ordinal,
                accepted_entity,
                payload,
            ) = parts
            item = QListWidgetItem(
                f"{int(ordinal):02d}  {proposal_type.upper():<14} {state.upper():<10}  {payload}"
            )
            item.setToolTip(
                f"{proposal_id}\nevidence={evidence_kind}:{evidence_ordinal}"
                f"\naccepted_entity={accepted_entity}"
            )
            item.setData(Qt.ItemDataRole.UserRole, proposal_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, state)
            item.setData(Qt.ItemDataRole.UserRole + 2, proposal_type)
            self.proposal_list.addItem(item)
            if proposal_id == selected:
                selected_item = item
        self.proposal_list.blockSignals(False)
        if selected_item is not None:
            self.proposal_list.setCurrentItem(selected_item)
        elif self.proposal_list.count() > 0:
            self.proposal_list.setCurrentRow(0)
        else:
            self._selected_proposal_id = None
        self._sync_proposal_actions()

    def _proposal_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        proposal_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_proposal_id = str(proposal_id) if proposal_id else None
        self._sync_proposal_actions()

    @Slot(QProcess.ProcessError)
    def _process_error(self, error: QProcess.ProcessError) -> None:
        self._operation = ""
        self._operation_job_id = None
        self._set_extension_controls(True)
        self.proposal_status.setText(
            "Unable to start ResearchResult command."
            if error == QProcess.ProcessError.FailedToStart
            else f"ResearchResult command error: {error.name}"
        )

    def _apply_job_filter(self, text: str) -> None:
        terms = tuple(part for part in text.casefold().split() if part)
        for index in range(self.workspace.jobs.count()):
            item = self.workspace.jobs.item(index)
            haystack = (item.text() + " " + item.toolTip()).casefold()
            item.setHidden(bool(terms) and not all(term in haystack for term in terms))

    def _base_process_finished(self, *_args: object) -> None:
        QTimer.singleShot(0, self._sync_job_actions)
        QTimer.singleShot(0, lambda: self._apply_job_filter(self.job_filter.text()))

    @Slot()
    def _periodic_refresh(self) -> None:
        if (
            self.workspace.isVisible()
            and not self.workspace._busy()
            and not self._busy()
        ):
            self.workspace.refresh()


def install_research_results_extension(
    workspace: ResearchWorkspace,
) -> ResearchResultsExtension:
    """Attach result inspection and promotion to the durable Research workspace."""
    return ResearchResultsExtension(workspace)
