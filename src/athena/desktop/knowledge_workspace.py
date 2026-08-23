"""Live KNOWLEDGE workspace for the native pATHENA desktop shell."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
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
    """Session knowledge inbox backed by the real extraction/review API signals."""

    def __init__(self, window: object, controller: DesktopApiController | None) -> None:
        super().__init__()
        self._window = window
        self._controller = controller
        self._source_chat_id: str | None = None
        self.setObjectName("knowledgeWorkspace")

        self.state = QLabel("IDLE")
        self.state.setObjectName("knowledgeReviewState")
        self.summary = QLabel(
            "No Knowledge extraction has been started in this desktop session."
        )
        self.summary.setObjectName("settingsHelp")
        self.summary.setWordWrap(True)
        self.source = QLabel("SOURCE CHAT  —")
        self.source.setProperty("role", "section")
        self.runtime = QLabel("CORE  —  /  CHATS  —")
        self.runtime.setObjectName("settingsHelp")

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

        self.items_widget = QWidget()
        self.items_widget.setObjectName("knowledgeWorkspaceItems")
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 8, 0)
        self.items_layout.setSpacing(10)
        self.items_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("knowledgeWorkspaceScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self.items_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 0, 18, 28)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("KNOWLEDGE / REVIEW INBOX")
        title.setObjectName("speaker")
        header.addWidget(title)
        header.addWidget(self.state)
        header.addStretch(1)
        header.addWidget(self.open_chat_button)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)

        intro = QLabel(
            "Live proposals produced by ADD TO KNOWLEDGE. Extraction stays attached "
            "to the exact persisted message revision; canonical merge decisions are "
            "resolved through the existing local Knowledge review API."
        )
        intro.setObjectName("settingsHelp")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self.runtime)
        layout.addWidget(self.source)
        layout.addWidget(self.summary)
        layout.addWidget(scroll, 1)

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
    """Replace the KNOWLEDGE shell placeholder with the live review inbox."""
    pages = getattr(window, "pages", None)
    if pages is None or pages.count() <= 1:
        raise RuntimeError("pATHENA desktop KNOWLEDGE page is unavailable")

    placeholder = pages.widget(1)
    workspace = KnowledgeWorkspace(window, controller)
    pages.removeWidget(placeholder)
    pages.insertWidget(1, workspace)
    placeholder.deleteLater()
    return workspace
