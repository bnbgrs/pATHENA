from __future__ import annotations

from PySide6.QtWidgets import QApplication, QListWidget, QPushButton, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import (
    _sync_dynamic_workspace_copy,
    apply_workspace_presentation,
)


def _app() -> QApplication:
    return create_application(["pathena-relation-presentation-test"])


def test_claim_relations_and_decision_copy_remain_humanized() -> None:
    app = _app()
    window = QWidget()
    knowledge = QWidget(window)
    knowledge.setObjectName("knowledgeWorkspace")

    relations = QListWidget(knowledge)
    relations.setObjectName("claimRelationList")
    relations.addItem(
        "CONTRADICTS    CLAIM    OBSERVATION   The related canonical claim"
    )

    open_related = QPushButton("OPEN RELATED CLAIM", knowledge)
    open_related.setEnabled(False)
    primary = QPushButton("MERGE", knowledge)
    secondary = QPushButton("KEEP SEPARATE", knowledge)

    try:
        apply_workspace_presentation(window)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert relations.item(0).text() == (
            "Contradicts · Claim · Observation · The related canonical claim"
        )
        assert open_related.text() == "Open related claim"
        assert open_related.objectName() == "openRelatedClaimButton"
        assert open_related.isHidden()
        assert primary.text() == "Merge"
        assert secondary.text() == "Keep separate"

        primary.setText("ACCEPT CONTRADICTION")
        secondary.setText("REJECT")
        open_related.setEnabled(True)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert primary.text() == "Confirm contradiction"
        assert secondary.text() == "Reject"
        assert open_related.isHidden() is False
    finally:
        window.close()
        app.processEvents()
