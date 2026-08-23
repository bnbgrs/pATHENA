"""Human review panel for pending model-proposed Claim contradictions."""

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


class ContradictionReviewsPanel(QWidget):
    """Require an explicit user decision before contradiction evidence is canonical."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("contradictionReviewsPanel")
        self._selected_review_id: str | None = None
        self._operation = ""
        self._buffer = ""

        self.status = QLabel("Loading pending contradiction reviews …")
        self.status.setObjectName("settingsHelp")

        self.refresh_button = QPushButton("REFRESH REVIEWS")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.clicked.connect(self.refresh_reviews)

        self.accept_button = QPushButton("CONFIRM CONTRADICTION")
        self.accept_button.setObjectName("newChatButton")
        self.accept_button.setEnabled(False)
        self.accept_button.setToolTip(
            "Create reciprocal canonical CONTRADICTS evidence for the exact reviewed Claim revisions"
        )
        self.accept_button.clicked.connect(self.accept_selected)

        self.reject_button = QPushButton("NOT A CONTRADICTION")
        self.reject_button.setObjectName("newChatButton")
        self.reject_button.setEnabled(False)
        self.reject_button.setToolTip(
            "Reject this model-proposed contradiction without creating Claim evidence"
        )
        self.reject_button.clicked.connect(self.reject_selected)

        self.review_list = QListWidget()
        self.review_list.setObjectName("pendingContradictionReviews")
        self.review_list.setMinimumWidth(390)
        self.review_list.currentItemChanged.connect(self._selection_changed)

        self.review_details = QPlainTextEdit()
        self.review_details.setObjectName("contradictionReviewDetails")
        self.review_details.setReadOnly(True)
        self.review_details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.review_details.setPlaceholderText(
            "Select a pending contradiction to inspect both exact Claim revisions."
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
        left_heading = QLabel("PENDING CONTRADICTIONS")
        left_heading.setProperty("role", "section")
        left_layout.addWidget(left_heading)
        left_layout.addWidget(self.status)
        left_layout.addWidget(self.review_list, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        detail_header = QHBoxLayout()
        detail_heading = QLabel("EXACT REVIEW BASIS")
        detail_heading.setProperty("role", "section")
        detail_header.addWidget(detail_heading)
        detail_header.addStretch(1)
        detail_header.addWidget(self.refresh_button)
        right_layout.addLayout(detail_header)
        right_layout.addWidget(self.review_details, 1)

        decision_row = QHBoxLayout()
        decision_row.addStretch(1)
        decision_row.addWidget(self.reject_button)
        decision_row.addWidget(self.accept_button)
        right_layout.addLayout(decision_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        intro = QLabel(
            "Model-reported contradictions never become canonical automatically. Compare the exact "
            "Claim revisions, then explicitly confirm or reject the relationship."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(splitter, 1)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(15_000)
        self._refresh_timer.timeout.connect(self._refresh_if_visible)
        self._refresh_timer.start()
        QTimer.singleShot(0, self.refresh_reviews)

    def refresh_reviews(self) -> None:
        if self._busy():
            return
        self._start(
            "list",
            ["list", "--limit", "200"],
            "Refreshing pending contradiction reviews",
        )

    def accept_selected(self) -> None:
        self._resolve_selected("accept")

    def reject_selected(self) -> None:
        self._resolve_selected("reject")

    def _resolve_selected(self, operation: str) -> None:
        if self._busy() or not self._selected_review_id:
            return
        self.review_details.clear()
        label = (
            "Confirming contradiction"
            if operation == "accept"
            else "Rejecting contradiction proposal"
        )
        self._start(operation, [operation, self._selected_review_id], label)

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        review_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_review_id = str(review_id) if review_id else None
        self._set_decision_buttons()
        if self._selected_review_id and not self._busy():
            self.review_details.clear()
            self._start(
                "show",
                ["show", self._selected_review_id],
                "Loading exact contradiction review basis",
            )

    def _set_decision_buttons(self) -> None:
        enabled = bool(self._selected_review_id) and not self._busy()
        self.accept_button.setEnabled(enabled)
        self.reject_button.setEnabled(enabled)

    def _refresh_if_visible(self) -> None:
        if self.isVisible() and not self._busy():
            self.refresh_reviews()

    def _busy(self) -> bool:
        return self._process.state() != QProcess.ProcessState.NotRunning

    def _start(self, operation: str, arguments: list[str], label: str) -> None:
        self._operation = operation
        self._buffer = ""
        self.status.setText(label + " …")
        self.refresh_button.setEnabled(False)
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self._process.start(
            sys.executable,
            ["-m", "athena.desktop.contradiction_reviews_cli", *arguments],
        )

    def _drain_output(self) -> None:
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._buffer += chunk
        if self._operation != "list":
            self.review_details.moveCursor(QTextCursor.MoveOperation.End)
            self.review_details.insertPlainText(chunk)

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

        if exit_code != 0:
            self.status.setText(f"Review command failed (exit {exit_code}).")
            if operation == "list":
                self.review_details.setPlainText(output)
            self._set_decision_buttons()
            return

        if operation == "list":
            self._render_list(output)
            self.status.setText(
                f"Pending contradictions: {self.review_list.count()} review(s)."
            )
            return
        if operation == "show":
            self.status.setText("Exact Claim revisions loaded; explicit decision required.")
            self._set_decision_buttons()
            return

        if operation in {"accept", "reject"}:
            self._selected_review_id = None
            self.status.setText(
                "Contradiction confirmed; canonical evidence created."
                if operation == "accept"
                else "Contradiction proposal rejected; no contradiction evidence created."
            )
            QTimer.singleShot(0, self.refresh_reviews)

    def _render_list(self, output: str) -> None:
        selected = self._selected_review_id
        self.review_list.blockSignals(True)
        self.review_list.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 6)
            if len(parts) != 7:
                continue
            review_id, confidence, _created, left_id, right_id, left, right = parts
            try:
                confidence_text = f"{float(confidence):.0%}"
            except ValueError:
                confidence_text = confidence
            item = QListWidgetItem(
                f"{confidence_text:<5}  {left}  ↔  {right}"
            )
            item.setToolTip(
                f"Review {review_id}\nLeft Claim {left_id}\nRight Claim {right_id}"
            )
            item.setData(Qt.ItemDataRole.UserRole, review_id)
            self.review_list.addItem(item)
            if review_id == selected:
                item_to_select = item

        self.review_list.blockSignals(False)
        if item_to_select is not None:
            self.review_list.setCurrentItem(item_to_select)
            self._selection_changed(item_to_select, None)
        elif self.review_list.count():
            self.review_list.setCurrentRow(0)
        else:
            self._selected_review_id = None
            self.accept_button.setEnabled(False)
            self.reject_button.setEnabled(False)
            self.review_details.setPlainText(
                "No pending contradiction reviews. Model proposals remain non-canonical until "
                "explicitly confirmed here."
            )

    def _process_error(self, error: QProcess.ProcessError) -> None:
        self._operation = ""
        self.refresh_button.setEnabled(True)
        self._set_decision_buttons()
        if error == QProcess.ProcessError.FailedToStart:
            self.status.setText("Unable to start the local contradiction review command.")
        else:
            self.status.setText(f"Contradiction review command error: {error.name}")
