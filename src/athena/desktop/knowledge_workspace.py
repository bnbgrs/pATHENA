"""Persistent KNOWLEDGE workspace for the native pATHENA desktop shell."""

from __future__ import annotations

import sys

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.api.contracts import (
    KnowledgeMergeReviewResponse,
    KnowledgeReviewResponse,
    MessageKnowledgeExtractionResponse,
)
from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.knowledge_review import (
    KnowledgeReviewError,
    parse_knowledge_entity_review,
    render_knowledge_entity_review,
)


class KnowledgeWorkspace(QWidget):
    """Browse durable canonical memory while preserving the live review inbox."""

    def __init__(self, window: object, controller: DesktopApiController | None) -> None:
        super().__init__()
        self._window = window
        self._controller = controller
        self._source_chat_id: str | None = None
        self._selected_knowledge_id: str | None = None
        self._selected_claim_id: str | None = None
        self._selected_review_id: str | None = None
        self._knowledge_operation = ""
        self._knowledge_buffer = ""
        self.setObjectName("knowledgeWorkspace")

        self.state = QLabel("IDLE")
        self.state.setObjectName("knowledgeReviewState")
        self.summary = QLabel(
            "Canonical memory is available below. Session proposals remain isolated until "
            "explicit review and acceptance."
        )
        self.summary.setObjectName("settingsHelp")
        self.summary.setWordWrap(True)
        self.source = QLabel("SOURCE CHAT  —")
        self.source.setProperty("role", "section")
        self.runtime = QLabel("CORE  —  /  CHATS  —")
        self.runtime.setObjectName("settingsHelp")
        self.browser_status = QLabel("Loading canonical memory …")
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

        self.refresh_knowledge_button = QPushButton("REFRESH VIEW")
        self.refresh_knowledge_button.setObjectName("newChatButton")
        self.refresh_knowledge_button.clicked.connect(self.refresh_knowledge)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("knowledgeSearchInput")
        self.search_input.setPlaceholderText(
            "Filter canonical knowledge, claims, or pending decisions…"
        )
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._apply_filter)

        self.history_button = QPushButton("HISTORY")
        self.history_button.setObjectName("newChatButton")
        self.history_button.setEnabled(False)
        self.history_button.clicked.connect(self.show_history)

        self.claim_history_button = QPushButton("HISTORY")
        self.claim_history_button.setObjectName("newChatButton")
        self.claim_history_button.setEnabled(False)
        self.claim_history_button.clicked.connect(self.show_claim_history)

        self.review_accept_button = QPushButton("ACCEPT CONTRADICTION")
        self.review_accept_button.setObjectName("newChatButton")
        self.review_accept_button.setEnabled(False)
        self.review_accept_button.setToolTip(
            "Create reciprocal contradiction evidence for the selected pending review"
        )
        self.review_accept_button.clicked.connect(self.accept_selected_review)

        self.review_reject_button = QPushButton("REJECT")
        self.review_reject_button.setObjectName("newChatButton")
        self.review_reject_button.setEnabled(False)
        self.review_reject_button.setToolTip(
            "Reject the selected pending contradiction without creating semantic evidence"
        )
        self.review_reject_button.clicked.connect(self.reject_selected_review)

        self.knowledge_list = QListWidget()
        self.knowledge_list.setObjectName("persistentKnowledgeList")
        self.knowledge_list.setMinimumWidth(360)
        self.knowledge_list.currentItemChanged.connect(self._knowledge_selection_changed)

        self.knowledge_details = QPlainTextEdit()
        self.knowledge_details.setObjectName("persistentKnowledgeDetails")
        self.knowledge_details.setReadOnly(True)
        self.knowledge_details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.knowledge_details.setPlaceholderText(
            "Select a durable KnowledgeUnit to inspect its current revision and provenance."
        )

        self.claim_list = QListWidget()
        self.claim_list.setObjectName("persistentClaimList")
        self.claim_list.setMinimumWidth(360)
        self.claim_list.currentItemChanged.connect(self._claim_selection_changed)

        self.claim_details = QPlainTextEdit()
        self.claim_details.setObjectName("persistentClaimDetails")
        self.claim_details.setReadOnly(True)
        self.claim_details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.claim_details.setPlaceholderText(
            "Select a canonical Claim to inspect statement, evidence, provenance and revision."
        )

        self.review_list = QListWidget()
        self.review_list.setObjectName("semanticReviewList")
        self.review_list.setMinimumWidth(360)
        self.review_list.currentItemChanged.connect(self._review_selection_changed)

        self.review_details = QPlainTextEdit()
        self.review_details.setObjectName("semanticReviewDetails")
        self.review_details.setReadOnly(True)
        self.review_details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.review_details.setPlaceholderText(
            "Pending contradiction decisions appear here after canonical proposal acceptance."
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

        self.browser_tabs = QTabWidget()
        self.browser_tabs.setObjectName("canonicalMemoryTabs")
        self.browser_tabs.currentChanged.connect(self._tab_changed)
        self.browser_tabs.addTab(self._build_knowledge_tab(), "Knowledge")
        self.browser_tabs.addTab(self._build_claims_tab(), "Claims")
        self.browser_tabs.addTab(self._build_reviews_tab(), "Decisions")
        self.browser_tabs.addTab(review_scroll, "Session review")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(12)

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
            "KnowledgeUnits, canonical Claims, evidence and semantic decisions remain durable "
            "across restarts. Model proposals stay in Session review until explicitly accepted."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.runtime)
        layout.addWidget(self.source)
        layout.addWidget(self.summary)
        layout.addWidget(self.search_input)
        layout.addWidget(self.browser_status)
        layout.addWidget(self.browser_tabs, 1)

        self._knowledge_refresh_timer = QTimer(self)
        self._knowledge_refresh_timer.setInterval(15_000)
        self._knowledge_refresh_timer.timeout.connect(self._refresh_knowledge_if_visible)
        self._knowledge_refresh_timer.start()
        QTimer.singleShot(0, self.refresh_knowledge)

    def _build_knowledge_tab(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 8, 8, 0)
        left_layout.setSpacing(8)
        heading = QLabel("CURRENT CANONICAL KNOWLEDGE")
        heading.setProperty("role", "section")
        left_layout.addWidget(heading)
        left_layout.addWidget(self.knowledge_list, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 0, 0)
        right_layout.setSpacing(8)
        detail_header = QHBoxLayout()
        detail_heading = QLabel("SELECTED KNOWLEDGE / PROVENANCE")
        detail_heading.setProperty("role", "section")
        detail_header.addWidget(detail_heading)
        detail_header.addStretch(1)
        detail_header.addWidget(self.history_button)
        right_layout.addLayout(detail_header)
        right_layout.addWidget(self.knowledge_details, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        return splitter

    def _build_claims_tab(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 8, 8, 0)
        left_layout.setSpacing(8)
        heading = QLabel("CURRENT CANONICAL CLAIMS")
        heading.setProperty("role", "section")
        left_layout.addWidget(heading)
        left_layout.addWidget(self.claim_list, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 0, 0)
        right_layout.setSpacing(8)
        detail_header = QHBoxLayout()
        detail_heading = QLabel("SELECTED CLAIM / EVIDENCE / PROVENANCE")
        detail_heading.setProperty("role", "section")
        detail_header.addWidget(detail_heading)
        detail_header.addStretch(1)
        detail_header.addWidget(self.claim_history_button)
        right_layout.addLayout(detail_header)
        right_layout.addWidget(self.claim_details, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        return splitter

    def _build_reviews_tab(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 8, 8, 0)
        left_layout.setSpacing(8)
        heading = QLabel("PENDING CONTRADICTION DECISIONS")
        heading.setProperty("role", "section")
        left_layout.addWidget(heading)
        left_layout.addWidget(self.review_list, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 0, 0)
        right_layout.setSpacing(8)
        detail_header = QHBoxLayout()
        detail_heading = QLabel("DECISION / BOTH CLAIMS")
        detail_heading.setProperty("role", "section")
        detail_header.addWidget(detail_heading)
        detail_header.addStretch(1)
        detail_header.addWidget(self.review_reject_button)
        detail_header.addWidget(self.review_accept_button)
        right_layout.addLayout(detail_header)
        right_layout.addWidget(self.review_details, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        return splitter

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
        self.browser_tabs.setCurrentIndex(3)

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
        self.browser_tabs.setCurrentIndex(3)

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
        """Refresh the canonical view currently visible to the user."""
        if self._knowledge_busy():
            return
        tab = self.browser_tabs.currentIndex()
        if tab == 1:
            self._start_knowledge(
                "claims-list",
                ["claims-list", "--limit", "200"],
                "Refreshing canonical Claims",
            )
            return
        if tab == 2:
            self._start_knowledge(
                "reviews-list",
                ["reviews-list", "--type", "contradiction", "--limit", "200"],
                "Refreshing pending contradiction decisions",
            )
            return
        if tab == 3:
            self.browser_status.setText("Session review is event-driven from the selected chat.")
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
            "Loading immutable Knowledge revision history",
        )

    def show_claim_history(self) -> None:
        if self._knowledge_busy() or not self._selected_claim_id:
            return
        self.claim_details.clear()
        self._start_knowledge(
            "claim-history",
            ["claim-history", self._selected_claim_id],
            "Loading immutable Claim revision history",
        )

    def accept_selected_review(self) -> None:
        self._resolve_selected_review(accept=True)

    def reject_selected_review(self) -> None:
        self._resolve_selected_review(accept=False)

    def _resolve_selected_review(self, *, accept: bool) -> None:
        if self._knowledge_busy() or not self._selected_review_id:
            return
        operation = "review-accept" if accept else "review-reject"
        label = "Accepting contradiction" if accept else "Rejecting contradiction"
        self.review_details.clear()
        self._start_knowledge(
            operation,
            [operation, self._selected_review_id],
            label,
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

    def _claim_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        claim_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_claim_id = str(claim_id) if claim_id else None
        self.claim_history_button.setEnabled(
            bool(self._selected_claim_id) and not self._knowledge_busy()
        )
        if self._selected_claim_id and not self._knowledge_busy():
            self.claim_details.clear()
            self._start_knowledge(
                "claim-show",
                ["claim-show", self._selected_claim_id],
                "Loading canonical Claim evidence",
            )

    def _review_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        review_id = None if current is None else current.data(Qt.ItemDataRole.UserRole)
        self._selected_review_id = str(review_id) if review_id else None
        enabled = bool(self._selected_review_id) and not self._knowledge_busy()
        self.review_accept_button.setEnabled(enabled)
        self.review_reject_button.setEnabled(enabled)
        if self._selected_review_id and not self._knowledge_busy():
            self.review_details.clear()
            self._start_knowledge(
                "review-show",
                ["review-show", self._selected_review_id],
                "Loading semantic decision",
            )

    def _tab_changed(self, _index: int) -> None:
        self._apply_filter(self.search_input.text())
        QTimer.singleShot(0, self.refresh_knowledge)

    def _apply_filter(self, text: str) -> None:
        needle = " ".join(text.casefold().split())
        for widget in (self.knowledge_list, self.claim_list, self.review_list):
            for index in range(widget.count()):
                item = widget.item(index)
                haystack = (item.text() + " " + item.toolTip()).casefold()
                item.setHidden(bool(needle) and needle not in haystack)

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
        self.claim_history_button.setEnabled(False)
        self.review_accept_button.setEnabled(False)
        self.review_reject_button.setEnabled(False)
        self._knowledge_process.start(
            sys.executable,
            ["-m", "athena.desktop.knowledge_cli", *arguments],
        )

    def _detail_target(self) -> QPlainTextEdit | None:
        if self._knowledge_operation in {"show", "history"}:
            return self.knowledge_details
        if self._knowledge_operation in {"claim-show", "claim-history"}:
            return self.claim_details
        if self._knowledge_operation in {
            "review-show",
            "review-accept",
            "review-reject",
        }:
            return self.review_details
        return None

    def _drain_knowledge_output(self) -> None:
        chunk = bytes(self._knowledge_process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if not chunk:
            return
        self._knowledge_buffer += chunk
        target = self._detail_target()
        if target is not None:
            target.moveCursor(QTextCursor.MoveOperation.End)
            target.insertPlainText(chunk)

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
        self.claim_history_button.setEnabled(bool(self._selected_claim_id))
        review_enabled = bool(self._selected_review_id)
        self.review_accept_button.setEnabled(review_enabled)
        self.review_reject_button.setEnabled(review_enabled)

        if exit_code != 0:
            self.browser_status.setText(f"Canonical memory command failed (exit {exit_code}).")
            target = self._detail_target_for_operation(operation)
            if target is not None and output and not target.toPlainText():
                target.setPlainText(output)
            return

        if operation in {"show", "claim-show"}:
            target = self._detail_target_for_operation(operation)
            if target is not None:
                try:
                    review = parse_knowledge_entity_review(output)
                except KnowledgeReviewError as exc:
                    target.setProperty("pathenaKnowledgeReviewState", "error")
                    target.setPlainText(
                        f"PERSISTED DETAIL UNAVAILABLE\n{exc}\n\nRaw command output:\n{output}"
                    )
                    self.browser_status.setText("Persisted detail could not be verified.")
                    return
                target.setPlainText(render_knowledge_entity_review(review))
                target.setProperty("pathenaKnowledgeReviewState", "ready")
                target.setProperty("pathenaKnowledgeEntityId", review.entity_id)

        if operation == "list":
            self._render_knowledge_list(output)
            self.browser_status.setText(
                f"Canonical Knowledge: {self.knowledge_list.count()} shown."
            )
        elif operation == "claims-list":
            self._render_claim_list(output)
            self.browser_status.setText(
                f"Canonical Claims: {self.claim_list.count()} shown."
            )
        elif operation == "reviews-list":
            self._render_review_list(output)
            self.browser_status.setText(
                f"Pending contradiction decisions: {self.review_list.count()} shown."
            )
        elif operation == "show":
            self.browser_status.setText("Current Knowledge revision and provenance loaded.")
        elif operation == "history":
            self.browser_status.setText("Immutable Knowledge history loaded.")
        elif operation == "claim-show":
            self.browser_status.setText("Current Claim evidence and provenance loaded.")
        elif operation == "claim-history":
            self.browser_status.setText("Immutable Claim history loaded.")
        elif operation == "review-show":
            self.browser_status.setText("Pending contradiction decision loaded.")
        elif operation in {"review-accept", "review-reject"}:
            self._selected_review_id = None
            self.review_accept_button.setEnabled(False)
            self.review_reject_button.setEnabled(False)
            action = "accepted" if operation == "review-accept" else "rejected"
            self.browser_status.setText(f"Contradiction decision {action}.")
            QTimer.singleShot(150, self.refresh_knowledge)

    def _detail_target_for_operation(self, operation: str) -> QPlainTextEdit | None:
        if operation in {"show", "history"}:
            return self.knowledge_details
        if operation in {"claim-show", "claim-history"}:
            return self.claim_details
        if operation in {"review-show", "review-accept", "review-reject"}:
            return self.review_details
        return None

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
        self._restore_or_select_first(
            self.knowledge_list,
            item_to_select,
            empty_callback=self._empty_knowledge,
        )
        self._apply_filter(self.search_input.text())

    def _render_claim_list(self, output: str) -> None:
        selected = self._selected_claim_id
        self.claim_list.blockSignals(True)
        self.claim_list.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 5)
            if len(parts) != 6:
                continue
            claim_id, revision_no, kind, status, lifecycle, statement = parts
            item = QListWidgetItem(
                f"{kind.upper():<18} R{revision_no:<3} {status.upper():<13}  {statement}"
            )
            item.setToolTip(
                f"{claim_id}\nlifecycle={lifecycle}\nkind={kind}\nstatus={status}"
            )
            item.setData(Qt.ItemDataRole.UserRole, claim_id)
            self.claim_list.addItem(item)
            if selected == claim_id:
                item_to_select = item

        self.claim_list.blockSignals(False)
        self._restore_or_select_first(
            self.claim_list,
            item_to_select,
            empty_callback=self._empty_claims,
        )
        self._apply_filter(self.search_input.text())

    def _render_review_list(self, output: str) -> None:
        selected = self._selected_review_id
        self.review_list.blockSignals(True)
        self.review_list.clear()
        item_to_select: QListWidgetItem | None = None

        for raw_line in output.splitlines():
            parts = raw_line.split("\t", 6)
            if len(parts) != 7:
                continue
            review_id, review_type, status, confidence, left_id, right_id, reason = parts
            try:
                confidence_percent = float(confidence) * 100
            except ValueError:
                confidence_percent = 0.0
            item = QListWidgetItem(
                f"{confidence_percent:5.1f}%  {review_type.upper():<14}  {reason}"
            )
            item.setToolTip(
                f"{review_id}\nstatus={status}\nleft={left_id}\nright={right_id}"
            )
            item.setData(Qt.ItemDataRole.UserRole, review_id)
            self.review_list.addItem(item)
            if selected == review_id:
                item_to_select = item

        self.review_list.blockSignals(False)
        self._restore_or_select_first(
            self.review_list,
            item_to_select,
            empty_callback=self._empty_reviews,
        )
        self._apply_filter(self.search_input.text())

    def _restore_or_select_first(
        self,
        widget: QListWidget,
        selected: QListWidgetItem | None,
        *,
        empty_callback: object,
    ) -> None:
        if selected is not None:
            widget.setCurrentItem(selected)
            if widget is self.knowledge_list:
                self._knowledge_selection_changed(selected, None)
            elif widget is self.claim_list:
                self._claim_selection_changed(selected, None)
            else:
                self._review_selection_changed(selected, None)
        elif widget.count() > 0:
            widget.setCurrentRow(0)
        elif callable(empty_callback):
            empty_callback()

    def _empty_knowledge(self) -> None:
        self._selected_knowledge_id = None
        self.history_button.setEnabled(False)
        self.knowledge_details.setPlainText(
            "No canonical Knowledge exists yet. Use Add to knowledge on a persisted chat "
            "message; accepted proposals remain visible here across restarts."
        )

    def _empty_claims(self) -> None:
        self._selected_claim_id = None
        self.claim_history_button.setEnabled(False)
        self.claim_details.setPlainText(
            "No canonical Claims exist yet. Claims accepted from extraction or explicitly "
            "promoted from chat will appear here with evidence and provenance."
        )

    def _empty_reviews(self) -> None:
        self._selected_review_id = None
        self.review_accept_button.setEnabled(False)
        self.review_reject_button.setEnabled(False)
        self.review_details.setPlainText(
            "No pending contradiction decisions. pATHENA keeps model-reported contradictions "
            "non-canonical until an explicit user decision is recorded."
        )

    def _knowledge_process_error(self, error: QProcess.ProcessError) -> None:
        self._knowledge_operation = ""
        self.refresh_knowledge_button.setEnabled(True)
        self.history_button.setEnabled(bool(self._selected_knowledge_id))
        self.claim_history_button.setEnabled(bool(self._selected_claim_id))
        review_enabled = bool(self._selected_review_id)
        self.review_accept_button.setEnabled(review_enabled)
        self.review_reject_button.setEnabled(review_enabled)
        if error == QProcess.ProcessError.FailedToStart:
            self.browser_status.setText("Unable to start the local pATHENA Knowledge command.")
        else:
            self.browser_status.setText(f"Canonical memory command error: {error.name}")

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
    """Replace the KNOWLEDGE shell placeholder with the canonical-memory workbench."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 1:
        raise RuntimeError("pATHENA desktop KNOWLEDGE page is unavailable")

    placeholder = pages.widget(1)
    workspace = KnowledgeWorkspace(window, controller)
    pages.removeWidget(placeholder)
    pages.insertWidget(1, workspace)
    placeholder.deleteLater()
    return workspace
