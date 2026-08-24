from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.app import create_application
from athena.desktop.knowledge_acceptance import KnowledgeAcceptanceController
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    _sync,
    apply_knowledge_acceptance_presentation,
)


def _app() -> QApplication:
    return create_application(["pathena-knowledge-acceptance-presentation-test"])


def test_canonical_acceptance_only_appears_for_actionable_review() -> None:
    app = _app()
    workspace = QWidget()
    root = QVBoxLayout(workspace)
    header = QHBoxLayout()
    root.addLayout(header)
    workspace.state = QLabel("IDLE")
    workspace.summary = QLabel("")
    root.addWidget(workspace.state)
    root.addWidget(workspace.summary)

    controller = KnowledgeAcceptanceController(
        workspace=workspace,
        controller=None,
    )
    try:
        apply_knowledge_acceptance_presentation(controller)
        app.processEvents()

        assert controller.button.text() == "Add reviewed items"
        assert controller.button.objectName() == "knowledgeAcceptanceButton"
        assert controller.button.property("role") == "primary"
        assert controller.button.isHidden()

        controller.button.setEnabled(True)
        _sync(controller)
        assert controller.button.isHidden() is False

        workspace.state.setText("ACCEPTING / ATOMIC COMMIT")
        _sync(controller)
        assert workspace.state.text() == "Adding reviewed items…"

        workspace.state.setText("ACCEPTANCE FAILED / REVIEW AGAIN")
        _sync(controller)
        assert workspace.state.text() == "Review again"

        workspace.state.setText("ACCEPTED / CANONICAL")
        _sync(controller)
        assert workspace.state.text() == "Added to canonical memory"
    finally:
        workspace.close()
        app.processEvents()
