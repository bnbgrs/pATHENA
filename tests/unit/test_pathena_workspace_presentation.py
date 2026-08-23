from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation


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
    section = QLabel("CURRENT CANONICAL KNOWLEDGE", workspace)
    intro = QLabel(
        "Browse canonical Knowledge across restarts and inspect exact revision provenance.",
        workspace,
    )
    refresh = QPushButton("REFRESH KNOWLEDGE", workspace)
    details = QPlainTextEdit(workspace)
    details.setObjectName("persistentKnowledgeDetails")
    knowledge_list = QListWidget(workspace)
    knowledge_list.setObjectName("persistentKnowledgeList")

    for widget in (title, section, intro, refresh, details, knowledge_list):
        workspace_layout.addWidget(widget)
    layout.addWidget(workspace)

    original_refresh = refresh
    original_details = details
    original_list = knowledge_list

    try:
        apply_workspace_presentation(window)
        app.processEvents()

        assert title.isHidden()
        assert section.text() == "Canonical knowledge"
        assert intro.text().startswith("Browse durable knowledge")
        assert refresh is original_refresh
        assert refresh.text() == "Refresh"
        assert details is original_details
        assert details.placeholderText().startswith("Select a knowledge item")
        assert knowledge_list is original_list
        assert knowledge_list.minimumWidth() == 320
    finally:
        window.close()
        app.processEvents()
