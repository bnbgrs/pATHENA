from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import (
    _sync_dynamic_workspace_copy,
    apply_workspace_presentation,
)


def _app() -> QApplication:
    return create_application(["pathena-workspace-presentation-test"])


def test_workspace_presentation_changes_copy_without_replacing_controls() -> None:
    app = _app()
    window = QWidget()
    layout = QVBoxLayout(window)

    workspace = QWidget(window)
    workspace.setObjectName("knowledgeWorkspace")
    workspace_layout = QVBoxLayout(workspace)

    title = QLabel("KNOWLEDGE / CANONICAL MEMORY", workspace)
    knowledge_heading = QLabel("CURRENT CANONICAL KNOWLEDGE", workspace)
    knowledge_detail_heading = QLabel("SELECTED KNOWLEDGE / PROVENANCE", workspace)
    claim_heading = QLabel("CURRENT CANONICAL CLAIMS", workspace)
    claim_detail_heading = QLabel("SELECTED CLAIM / EVIDENCE / PROVENANCE", workspace)
    decision_heading = QLabel("PENDING CONTRADICTION DECISIONS", workspace)
    decision_detail_heading = QLabel("DECISION / BOTH CLAIMS", workspace)
    intro = QLabel(
        "Browse canonical Knowledge across restarts and inspect exact revision provenance.",
        workspace,
    )

    refresh = QPushButton("REFRESH KNOWLEDGE", workspace)
    confirm = QPushButton("ACCEPT CONTRADICTION", workspace)
    reject = QPushButton("REJECT", workspace)

    search = QLineEdit(workspace)
    search.setObjectName("knowledgeSearchInput")

    knowledge_details = QPlainTextEdit(workspace)
    knowledge_details.setObjectName("persistentKnowledgeDetails")
    claim_details = QPlainTextEdit(workspace)
    claim_details.setObjectName("persistentClaimDetails")
    decision_details = QPlainTextEdit(workspace)
    decision_details.setObjectName("semanticReviewDetails")

    knowledge_list = QListWidget(workspace)
    knowledge_list.setObjectName("persistentKnowledgeList")
    claim_list = QListWidget(workspace)
    claim_list.setObjectName("persistentClaimList")
    decision_list = QListWidget(workspace)
    decision_list.setObjectName("semanticReviewList")

    tabs = QTabWidget(workspace)
    tabs.setObjectName("canonicalMemoryTabs")
    for title_text in ("Knowledge", "Claims", "Decisions", "Session review"):
        tabs.addTab(QWidget(), title_text)

    for widget in (
        title,
        knowledge_heading,
        knowledge_detail_heading,
        claim_heading,
        claim_detail_heading,
        decision_heading,
        decision_detail_heading,
        intro,
        refresh,
        confirm,
        reject,
        search,
        knowledge_details,
        claim_details,
        decision_details,
        knowledge_list,
        claim_list,
        decision_list,
        tabs,
    ):
        workspace_layout.addWidget(widget)
    layout.addWidget(workspace)

    original_controls = {
        "refresh": refresh,
        "confirm": confirm,
        "reject": reject,
        "search": search,
        "knowledge_details": knowledge_details,
        "claim_details": claim_details,
        "decision_details": decision_details,
        "knowledge_list": knowledge_list,
        "claim_list": claim_list,
        "decision_list": decision_list,
        "tabs": tabs,
    }

    try:
        apply_workspace_presentation(window)
        app.processEvents()

        assert title.isHidden()
        assert knowledge_heading.text() == "Canonical knowledge"
        assert knowledge_detail_heading.text() == "Details & provenance"
        assert claim_heading.text() == "Canonical claims"
        assert claim_detail_heading.text() == "Evidence & provenance"
        assert decision_heading.text() == "Contradiction decisions"
        assert decision_detail_heading.text() == "Compare claims"
        assert intro.text().startswith("Browse durable knowledge, claims, evidence")

        assert refresh is original_controls["refresh"]
        assert refresh.text() == "Refresh"
        assert confirm is original_controls["confirm"]
        assert confirm.text() == "Confirm contradiction"
        assert reject is original_controls["reject"]
        assert reject.text() == "Reject"

        assert search is original_controls["search"]
        assert search.placeholderText() == "Search knowledge, claims, or decisions…"

        assert knowledge_details is original_controls["knowledge_details"]
        assert knowledge_details.placeholderText().startswith("Select a knowledge item")
        assert claim_details is original_controls["claim_details"]
        assert claim_details.placeholderText().startswith("Select a claim")
        assert decision_details is original_controls["decision_details"]
        assert decision_details.placeholderText().startswith("Select a pending decision")

        assert knowledge_list is original_controls["knowledge_list"]
        assert claim_list is original_controls["claim_list"]
        assert decision_list is original_controls["decision_list"]
        assert knowledge_list.minimumWidth() == 310
        assert claim_list.minimumWidth() == 310
        assert decision_list.minimumWidth() == 310

        assert tabs is original_controls["tabs"]
        assert [tabs.tabText(index) for index in range(tabs.count())] == [
            "Knowledge",
            "Claims",
            "Decisions",
            "From chat",
        ]
    finally:
        window.close()
        app.processEvents()


def test_dynamic_workspace_copy_stays_humanized_without_duplicate_sync_timers() -> None:
    app = _app()
    window = QWidget()
    workspace = QWidget(window)
    workspace.setObjectName("knowledgeWorkspace")

    state = QLabel("PREFLIGHT / PENDING", workspace)
    state.setObjectName("knowledgeReviewState")
    runtime = QLabel("CORE  READY  /  CHATS  4", workspace)
    source = QLabel("SOURCE CHAT  ABCDEF12  /  MESSAGE  12345678", workspace)

    try:
        apply_workspace_presentation(window)
        apply_workspace_presentation(window)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert state.text() == "Checking…"
        assert runtime.text() == "Core ready · 4 conversations"
        assert runtime.toolTip() == "CORE  READY  /  CHATS  4"
        assert source.text() == "From conversation · selected message"
        assert source.toolTip() == "SOURCE CHAT  ABCDEF12  /  MESSAGE  12345678"

        timers = window.findChildren(QTimer, "pathenaWorkspaceCopySync")
        assert len(timers) == 1
        assert timers[0].isActive()

        state.setText("REVIEW COMPLETE / READY")
        runtime.setText("CORE  DISCONNECTED  /  CHATS  —")
        _sync_dynamic_workspace_copy(window)
        assert state.text() == "Ready to add"
        assert runtime.text() == "Core unavailable"
    finally:
        window.close()
        app.processEvents()
