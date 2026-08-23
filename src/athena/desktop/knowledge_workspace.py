"""Persistent KNOWLEDGE workspace for the native pATHENA desktop shell."""

from __future__ import annotations

import sys

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from athena.api.contracts import (
    KnowledgeMergeReviewResponse,
    KnowledgeReviewResponse,
    MessageKnowledgeExtractionResponse,
)
from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot


class KnowledgeWorkspace(QWidget):
    """Browse durable Knowledge while preserving the live extraction/review inbox."""

    def __init__(self, window: object, controller: DesktopApiController | None) -> None:
        super().__init__()
        self._window = window
        self._controller = controller
        self._source_chat_id: str | None = None
        self._selected_knowledge_id: str | None = None
        self._knowledge_operation = ""
        self._knowledge_buffer = ""
        self.setObjectName("knowledgeWorkspace")

        self.state = QLabel("IDLE")
        self.state.setObjectName("knowledgeReviewState")
        self.summary = QLabel(
            "Review inbox is idle. Durable Knowledge remains available in the browser below."
        )
        self.summary.setObjectName("settingsHelp")
        self.summary.setWordWrap(True)
        self.source = QLabel("SOURCE CHAT  —")
        self.source.setProperty("role", "section")
        self.runtime = QLabel("CORE  —  /  CHATS  —")
        self.runtime.setObjectName("settingsHelp")
        self.browser_status = QLabel("Loading persistent Knowledge …")
        self.browser_status.setObjectName("settingsHelp")

        self.open_chat_button = QPushButton("OPEN SOURCE CHAT")
        self.open_chat_button.setObjectName("newChatButton")
        self.open_chat_button.setEnabled(False)
        self.open_chat_button.clicked.connect(self._open_source_chat)

        self.refresh_button = QPushButton("REFRESH CORE")
        self.refresh_button.setObjectName("newChatButton")
        self.refresh_button.setEnabled(controller is not None)
        if controller is not None:
            self.refresh_button.clicked.connect(controller.refresh)
            controller.snapshot_ready.connect(self.apply_snapshot)
            controller.connection_failed.connect(self.apply_failure)
            controller.knowledge_extraction_ready.connect(self.apply_extraction)
            controller.knowledge_review_ready.connect(self.apply_review)
            controller.knowledge_merge_review_ready.connect(self.apply_merge_review)

        self.refresh_knowledge_button = QPushButton("REFRESH KNOWLEDGE")
        self.refresh_knowledge_button.setObjectName("newChatButton")
        self.refresh_knowledge_button.clicked.connect(self.refresh_knowledge)

        self.history_button = QPushButton("HISTORY")
        self.history_button.setObjectName("newChatButton")
        self.history_button.setEnabled(False)
        self.history_button.clicked.connect(self.show_history)

        self.knowledge_list = QListWidget()
        self.knowledge_list.setObjectName("persistentKnowledgeList")
        self.knowledge_list.setMinimumWidth(390)
        self.knowledge_list.currentItemChanged.connect(self._knowledge_selection_changed)

        self.knowledge_details = QPlainTextEdit()
        self.knowledge_details.setObjectName("persistentKnowledgeDetails")
        self.knowledge_details.setReadOnly(True)
        self.knowledge_details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.knowledge_details.setPlaceholderText(
            "Select a durable KnowledgeUnit to inspect its current revision and provenance."
        )

        self._knowledge_process = QProcess(self)
        self._knowledge_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._knowledge_process.readyReadStandardOutput.connect(self._drain_knowledge_output)
        self._knowledge_process.finished.connect(self._knowledge_process_finished)
        self._knowledge_process.errorOccurred.connect(self._knowledge_process_error)

        self.items_widget = QWidget()
        self.items_widget.setObjectName("knowledgeWorkspaceItems")
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 8, 0)
        self.items_layout.setSpacing(10)
        self.items_layout.addStretch(1)

        review_scroll = QScrollArea()
        review_scroll.setObjectName("knowledgeWorkspaceScroll")
        review_scroll.setWidgetResizable(True)
        review_scroll.setFrameShape(QFrame.Shape.NoFrame)
        review_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        review_scroll.setWidget(self.items_widget)

        browser_splitter = QSplitter(Qt.Orientation.Horizontal)

        browser_left = QWidget()
        browser_left_layout = QVBoxLayout(browser_left)
        browser_left_layout.setContentsMargins(0, 0, 0, 0)
        browser_left_layout.setSpacing(8)
        current_heading = QLabel("CURRENT CANONICAL KNOWLEDGE")
        current_heading.setProperty("role", "section")
        browser_left_layout.addWidget(current_heading)
        browser_left_layout.addWidget(self.browser_status)
        browser_left_layout.addWidget(self.knowledge_list, 1)

        browser_right = QWidget()
        browser_right_layout = QVBoxLayout(browser_right)
        browser_right_layout.setContentsMargins(0, 0, 0, 0)
        browser_right_layout.setSpacing(8)
        detail_header = QHBoxLayout()
        detail_heading = QLabel("SELECTED KNOWLEDGE / PROVENANCE")
        detail_heading.setProperty("role", "section")
        detail_header.addWidget(detail_heading)
        detail_header.addStretch(1)
        detail_header.addWidget(self.history_button)
        browser_right_layout.addLayout(detail_header)
        browser_right_layout.addWidget(self.knowledge_details, 1)
        review_heading = QLabel("REVIEW INBOX / CURRENT SESSION")
        review_heading.setProperty("role", "section")
        browser_right_layout.addWidget(review_heading)
        browser_right_layout.addWidget(review_scroll, 1)

        browser_splitter.addWidget(browser_left)
        browser_splitter.addWidget(browser_right)
        browser_splitter.setStretchFactor(0, 1)
        browser_splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("KNOWLEDGE / CANONICAL MEMORY")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addWidget(self.state)
        header.addStretch(1)
        header.addWidget(self.open_chat_button)
        header.addWidget(self.refresh_knowledge_button)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)

        intro = QLabel(
            "Browse canonical Knowledge across restarts and inspect exact revision provenance. "
            "ADD TO KNOWLEDGE still feeds the live review inbox; merge decisions remain "
            "attached to the exact persisted chat-message revision."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.runtime)
        layout.addWidget(self.source)
        layout.addWidget(self.summary)
        layout.addWidget(browser_splitter, 1)

        self._knowledge_refresh_timer = QTimer(self)
        self._knowledge_refresh_timer.setInterval(15_000)
        self._knowledge_refresh_timer.timeout.connect(self._refresh_knowledge_if_visible)
        self._knowledge_refresh_timer.start()
        QTimer.singleShot(0, self.refresh_knowledge)

    def apply_snapshot(self, payload: object) -> None:
        if not isinstance(payload, DesktopApiSnapshot):
            return
        self.runtime.setText(
            f"CORE  {payload.health.core_status.upper()}  /  CHATS  {len(payload.chats)}"
        )

    def apply_failure(self, message: str) -> None:
        self.runtime.setText("CORE  DISCONNECTED  /  CHATS  —")
        self.state.setText("CORE UNAVAILABLE")
        self.summary.setText(message)

    def apply_extraction(self, payload: object) -> None:
        if not isinstance(payload, MessageKnowledgeExtractionResponse):
            return
        self._source_chat_id = payload.chat_id
        self.open_chat_button.setEnabled(True)
        self.source.setText(
            "SOURCE CHAT  "
            + payload.chat_id[:8].upper()
            + "  /  MESSAGE  "
            + payload.message_id[:8].upper()
        )
        self.state.setText("PREFLIGHT / PENDING")
        self.summary.setText(
            f"Run {payload.processing_run_id[:8].upper()} · {len(payload.knowledge_units)} "
            f"Knowledge · {len(payload.claims)} Claims · {len(payload.relations)} Relations"
        )
        self._clear_items()

        for knowledge_proposal in payload.knowledge_units:
            title = knowledge_proposal.title.strip() if knowledge_proposal.title else ""
            body = (
                knowledge_proposal.body
                if not title
                else f"{title}\n{knowledge_proposal.body}"
            )
            self._add_item(
                f"K{knowledge_proposal.proposal_index:02d} / "
                f"{knowledge_proposal.knowledge_kind.upper()} / "
                f"{knowledge_proposal.confidence:.0%}",
                body,
            )
        for claim_proposal in payload.claims:
            self._add_item(
                f"C{claim_proposal.proposal_index:02d} / "
                f"{claim_proposal.claim_kind.upper()} / "
                f"{claim_proposal.confidence:.0%}",
                claim_proposal.statement,
            )
        if payload.relations:
            self._add_item(
                "RELATIONS",
                "\n".join(
                    f"{relation.left_type[0].upper()}{relation.left_index:02d} "
                    f"{relation.relation_type.upper()} "
                    f"{relation.right_type[0].upper()}{relation.right_index:02d} "
                    f"/ {relation.confidence:.0%}"
                    for relation in payload.relations
                ),
            )
        if payload.extractor_merge_candidates:
            self._add_item(
                "EXTRACTOR MERGE CANDIDATES / BLOCKING",
                "\n".join(
                    f"{candidate.proposal_type.upper()} {candidate.proposal_index:02d} / "
                    f"{candidate.reason} / {candidate.confidence:.0%}"
                    for candidate in payload.extractor_merge_candidates
                ),
            )

    def apply_review(self, payload: object) -> None:
        if not isinstance(payload, KnowledgeReviewResponse):
            return
        if payload.ready_to_accept:
            self.state.setText("REVIEW COMPLETE / READY")
        elif payload.blocked_reason == "canonical_merge_candidates":
            self.state.setText("DECISION REQUIRED / CANONICAL MERGE")
        elif payload.blocked_reason == "extractor_merge_candidates":
            self.state.setText("BLOCKED / EXTRACTOR MERGE")
        else:
            self.state.setText("BLOCKED / REVIEW REQUIRED")

        decisions = tuple(payload.knowledge_decisions) + tuple(payload.claim_decisions)
        if decisions:
            lines: list[str] = []
            for decision in decisions:
                target = getattr(decision, "existing_entity_id", None)
                suffix = f" → {target[:8].upper()}" if isinstance(target, str) else ""
                prefix = "K" if decision in payload.knowledge_decisions else "C"
                lines.append(
                    f"{prefix}{decision.proposal_index:02d}  "
                    f"{decision.action.replace('_', ' ').upper()}{suffix}"
                )
            self._add_item("CANONICAL PREFLIGHT", "\n".join(lines))

        for candidate in payload.canonical_merge_candidates:
            self._add_item(
                f"MERGE REVIEW / {candidate.proposal_type.upper()} "
                f"{candidate.proposal_index:02d} / {candidate.similarity:.0%}",
                f"Existing {candidate.existing_entity_id[:8].upper()} · {candidate.reason}\n"
                "Open the source chat to resolve MERGE or KEEP SEPARATE.",
            )
        QTimer.singleShot(250, self.refresh_knowledge)

    def apply_merge_review(self, payload: object) -> None:
        if not isinstance(payload, KnowledgeMergeReviewResponse):
            return
        decision = payload.decision
        self.state.setText(
            "MERGE DECISION SAVED" if decision is not None else "DECISION REQUIRED"
        )
        if decision is not None:
            self._add_item(
                "CANONICAL MERGE DECISION",
                f"{payload.review_id[:8].upper()} · {decision.replace('_', ' ').upper()}",
            )
        QTimer.singleShot(250, self.refresh_knowledge)

    def refresh_knowledge(self) -> None:
        if self._knowledge_busy():
            return
        self._start_knowledge(
            "list",
            ["list", "--limit", "200"],
            "Refreshing canonical Knowledge",
        )

    def show_history(self) -> None:
        if self._knowledge_busy() or not self._selected_knowledge_id:
            return
        self.knowledge_details.clear()
        self._start_knowledge(
            "history",
            ["history", self._selected_knowledge_id],
            "Loading immutable revision history",
        )

    def _knowledge_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        knowledge_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_knowledge_id = str(knowledge_id) if knowledge_id else None
        self.history_button.setEnabled(
            bool(self._selected_knowledge_id) and not self._knowledge_busy()
        )
        if self._selected_knowledge_id and not self._knowledge_busy():
            self.knowledge_details.clear()
            self._start_knowledge(
                "show",
                ["show", self._selected_knowledge_id],
                "Loading canonical Knowledge",
            )

    def _refresh_knowledge_if_visible(self) -> None:
        if self.isVisible() and not self._knowledge_busy():
            self.refresh_knowledge()

    def _knowledge_busy(self) -> bool:
        return self._knowledge_process.state() != QProcess.ProcessState.NotRunning

    def _start_knowledge(
        self,
        operation: str,
        arguments: list[str],
        label: str,
    ) -> None:
        self._knowledge_operation = operation
        self._knowledge_buffer = ""
        self.browser_status.setText(label + " …")
        self.refresh_knowledge_button.setEnabled(False)
        self.history_button.setEnabled(False)
        self._knowledge_process.start(
            sys.executable,
            ["-m", "athena.desktop.knowledge_cli", *arguments],
        )

    def _drain_knowledge_output(self) -> None:
        chunk = bytes(self._knowledge_process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._knowledge_buffer += chunk
        if self._knowledge_operation != "list":
            self.knowledge_details.moveCursor(QTextCursor.MoveOperation.End)
            self.knowledge_details.insertPlainText(chunk)

    def _knowledge_process_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:
        self._drain_knowledge_output()
        operation = self._knowledge_operation
        output = self._knowledge_buffer
        self._knowledge_operation = ""
        self.refresh_knowledge_button.setEnabled(True)
        self.history_button.setEnabled(bool(self._selected_knowledge_id))

        if exit_code != 0:
            self.browser_status.setText(f"Knowledge command failed (exit {exit_code}).")
            if operation == "list":
                self.knowledge_details.setPlainText(output)
            return

        if operation == "list":
            self._render_knowledge_list(output)
            self.browser_status.setText(
                f"Canonical Knowledge refreshed: {self.knowledge_list.count()} shown."
            )
            return
        if operation == "show":
            self.browser_status.setText("Current Knowledge revision loaded.")
        elif operation == "history":
            self.browser_status.setText("Immutable Knowledge history loaded.")

    def _render_knowledge_list(self, output: str) -> None:
        selected = self._selected_knowledge_id
        self.knowledge_list.blockSignals(True)
        self.knowledge_list.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 5)
            if len(parts) != 6:
                continue
            knowledge_id, revision_no, kind, status, lifecycle, summary = parts
            item = QListWidgetItem(
                f"{kind.upper():<18} R{revision_no:<3} {status.upper():<13}  {summary}"
            )
            item.setToolTip(
                f"{knowledge_id}\nlifecycle={lifecycle}\nkind={kind}\nstatus={status}"
            )
            item.setData(Qt.ItemDataRole.UserRole, knowledge_id)
            self.knowledge_list.addItem(item)
            if selected == knowledge_id:
                item_to_select = item

        self.knowledge_list.blockSignals(False)
        if item_to_select is not None:
            self.knowledge_list.setCurrentItem(item_to_select)
            self._knowledge_selection_changed(item_to_select, None)
        elif self.knowledge_list.count() > 0:
            self.knowledge_list.setCurrentRow(0)
        else:
            self._selected_knowledge_id = None
            self.history_button.setEnabled(False)
            self.knowledge_details.setPlainText(
                "No canonical Knowledge exists yet. Use ADD TO KNOWLEDGE on a persisted "
                "chat message; accepted proposals will remain visible here across restarts."
            )

    def _knowledge_process_error(self, error: QProcess.ProcessError) -> None:
        self._knowledge_operation = ""
        self.refresh_knowledge_button.setEnabled(True)
        self.history_button.setEnabled(bool(self._selected_knowledge_id))
        if error == QProcess.ProcessError.FailedToStart:
            self.browser_status.setText("Unable to start the local pATHENA Knowledge command.")
        else:
            self.browser_status.setText(f"Knowledge command error: {error.name}")

    def _open_source_chat(self) -> None:
        chat_id = self._source_chat_id
        navigation = getattr(self._window, "navigation", None)
        if navigation is not None:
            navigation.setCurrentRow(0)
        if chat_id is not None and self._controller is not None:
            self._controller.load_chat(chat_id)

    def _clear_items(self) -> None:
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.items_layout.addStretch(1)

    def _add_item(self, title: str, body: str) -> None:
        card = QFrame()
        card.setObjectName("knowledgeReviewItem")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)
        heading = QLabel(title)
        heading.setObjectName("knowledgeReviewItemTitle")
        text = QLabel(body)
        text.setObjectName("knowledgeReviewItemBody")
        text.setTextFormat(Qt.TextFormat.PlainText)
        text.setWordWrap(True)
        text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(heading)
        layout.addWidget(text)
        self.items_layout.insertWidget(max(0, self.items_layout.count() - 1), card)


def install_knowledge_workspace(
    window: object,
    controller: DesktopApiController | None,
) -> KnowledgeWorkspace:
    """Replace the KNOWLEDGE shell placeholder with the durable browser + review inbox."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 1:
        raise RuntimeError("pATHENA desktop KNOWLEDGE page is unavailable")

    placeholder = pages.widget(1)
    workspace = KnowledgeWorkspace(window, controller)
    pages.removeWidget(placeholder)
    pages.insertWidget(1, workspace)
    placeholder.deleteLater()
    return workspace
