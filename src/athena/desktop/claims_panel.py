"""Canonical Claim browser embedded in the desktop Knowledge workspace."""

from __future__ import annotations

import sys

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class CanonicalClaimsPanel(QWidget):
    """Browse durable canonical Claims, evidence, and immutable revision history."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("canonicalClaimsPanel")
        self._selected_claim_id: str | None = None
        self._operation = ""
        self._buffer = ""

        self.status = QLabel("Loading canonical Claims …")
        self.status.setObjectName("settingsHelp")

        self.refresh_button = QPushButton("REFRESH CLAIMS")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.clicked.connect(self.refresh_claims)

        self.history_button = QPushButton("HISTORY")
        self.history_button.setObjectName("newChatButton")
        self.history_button.setEnabled(False)
        self.history_button.clicked.connect(self.show_history)

        self.claim_list = QListWidget()
        self.claim_list.setObjectName("persistentClaimsList")
        self.claim_list.setMinimumWidth(390)
        self.claim_list.currentItemChanged.connect(self._selection_changed)

        self.claim_details = QPlainTextEdit()
        self.claim_details.setObjectName("persistentClaimsDetails")
        self.claim_details.setReadOnly(True)
        self.claim_details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.claim_details.setPlaceholderText(
            "Select a canonical Claim to inspect its current revision, provenance, and evidence."
        )

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._drain_output)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        left_heading = QLabel("CURRENT CANONICAL CLAIMS")
        left_heading.setProperty("role", "section")
        left_layout.addWidget(left_heading)
        left_layout.addWidget(self.status)
        left_layout.addWidget(self.claim_list, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        detail_header = QHBoxLayout()
        detail_heading = QLabel("SELECTED CLAIM / EVIDENCE")
        detail_heading.setProperty("role", "section")
        detail_header.addWidget(detail_heading)
        detail_header.addStretch(1)
        detail_header.addWidget(self.history_button)
        detail_header.addWidget(self.refresh_button)
        right_layout.addLayout(detail_header)
        right_layout.addWidget(self.claim_details, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        intro = QLabel(
            "Canonical Claims are durable semantic assertions. Evidence remains explicit; "
            "contradictions are represented as evidence/review state rather than silently "
            "collapsing one side."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(splitter, 1)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(15_000)
        self._refresh_timer.timeout.connect(self._refresh_if_visible)
        self._refresh_timer.start()
        QTimer.singleShot(0, self.refresh_claims)

    def refresh_claims(self) -> None:
        if self._busy():
            return
        self._start(
            "list",
            ["list", "--limit", "200"],
            "Refreshing canonical Claims",
        )

    def show_history(self) -> None:
        if self._busy() or not self._selected_claim_id:
            return
        self.claim_details.clear()
        self._start(
            "history",
            ["history", self._selected_claim_id],
            "Loading immutable Claim history",
        )

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        claim_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_claim_id = str(claim_id) if claim_id else None
        self.history_button.setEnabled(bool(self._selected_claim_id) and not self._busy())
        if self._selected_claim_id and not self._busy():
            self.claim_details.clear()
            self._start(
                "show",
                ["show", self._selected_claim_id],
                "Loading canonical Claim",
            )

    def _refresh_if_visible(self) -> None:
        if self.isVisible() and not self._busy():
            self.refresh_claims()

    def _busy(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning

    def _start(self, operation: str, arguments: list[str], label: str) -> None:
        self._operation = operation
        self._buffer = ""
        self.status.setText(label + " …")
        self.refresh_button.setEnabled(False)
        self.history_button.setEnabled(False)
        self._process.start(
            sys.executable,
            ["-m", "athena.desktop.claims_cli", *arguments],
        )

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation != "list":
            self.claim_details.moveCursor(QTextCursor.MoveOperation.End)
            self.claim_details.insertPlainText(chunk)

    def _process_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:
        self._drain_output()
        operation = self._operation
        output = self._buffer
        self._operation = ""
        self.refresh_button.setEnabled(True)
        self.history_button.setEnabled(bool(self._selected_claim_id))

        if exit_code != 0:
            self.status.setText(f"Claim command failed (exit {exit_code}).")
            if operation == "list":
                self.claim_details.setPlainText(output)
            return

        if operation == "list":
            self._render_list(output)
            self.status.setText(f"Canonical Claims refreshed: {self.claim_list.count()} shown.")
            return
        if operation == "show":
            self.status.setText("Current Claim revision and evidence loaded.")
        elif operation == "history":
            self.status.setText("Immutable Claim history loaded.")

    def _render_list(self, output: str) -> None:
        selected = self._selected_claim_id
        self.claim_list.blockSignals(True)
        self.claim_list.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 5)
            if len(parts) != 6:
                continue
            claim_id, revision_no, kind, status, lifecycle, summary = parts
            item = QListWidgetItem(
                f"{kind.upper():<20} R{revision_no:<3} {status.upper():<13}  {summary}"
            )
            item.setToolTip(f"{claim_id}\nLifecycle: {lifecycle}")
            item.setData(Qt.ItemDataRole.UserRole, claim_id)
            self.claim_list.addItem(item)
            if claim_id == selected:
                item_to_select = item

        self.claim_list.blockSignals(False)
        if item_to_select is not None:
            self.claim_list.setCurrentItem(item_to_select)
            self._selection_changed(item_to_select, None)
        elif self.claim_list.count():
            self.claim_list.setCurrentRow(0)
        else:
            self._selected_claim_id = None
            self.history_button.setEnabled(False)
            self.claim_details.setPlainText(
                "No canonical Claims yet. Accepted extraction proposals appear here after commit."
            )

    def _process_error(self, error: QProcess.ProcessError) -> None:
        self._operation = ""
        self.refresh_button.setEnabled(True)
        self.history_button.setEnabled(bool(self._selected_claim_id))
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText("Unable to start the local Claim reader.")
        else:
            self.status.setText(f"Claim command error: {error.name}")


def install_claims_panel(knowledge_workspace: QWidget) -> CanonicalClaimsPanel:
    """Add Claims as a second canonical view without expanding primary navigation."""
    root = knowledge_workspace.layout()
    if not isinstance(root, QBoxLayout) or root.count() < 1:
        raise RuntimeError("Knowledge workspace layout is unavailable")

    browser_index = root.count() - 1
    browser_item = root.itemAt(browser_index)
    browser = None if browser_item is None else browser_item.widget()
    if browser is None:
        raise RuntimeError("Knowledge canonical browser is unavailable")

    tabs = QTabWidget(knowledge_workspace)
    tabs.setObjectName("canonicalKnowledgeTabs")
    root.removeWidget(browser)
    tabs.addTab(browser, "KNOWLEDGE")
    panel = CanonicalClaimsPanel()
    tabs.addTab(panel, "CLAIMS / EVIDENCE")
    root.insertWidget(browser_index, tabs, 1)
    return panel
