from __future__ import annotations

from PySide6.QtWidgets import QApplication, QListWidget, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import _sync_dynamic_workspace_copy


def _app() -> QApplication:
    return create_application(["pathena-list-presentation-test"])


def _list(window: QWidget, object_name: str, text: str) -> QListWidget:
    widget = QListWidget(window)
    widget.setObjectName(object_name)
    widget.addItem(text)
    return widget


def test_workspace_lists_replace_cli_padding_with_readable_metadata() -> None:
    app = _app()
    window = QWidget()

    knowledge = _list(
        window,
        "persistentKnowledgeList",
        "FACT               R3   ASSERTED       A durable fact",
    )
    claim = _list(
        window,
        "persistentClaimList",
        "OBSERVATION        R2   SUPPORTED      A supported claim",
    )
    decision = _list(
        window,
        "semanticReviewList",
        "89.0%  CONTRADICTION   Conflicting values",
    )
    research = _list(
        window,
        "researchJobList",
        "RUNNING             42.0%  Compare the sources",
    )
    jobs = _list(
        window,
        "durableJobList",
        "WAITING            P5  exhaustive_research       synthesis          Waiting for input",
    )
    files = _list(
        window,
        "sourceList",
        "READY                1.2 MiB  report.pdf",
    )
    backups = _list(
        window,
        "backupSnapshotList",
        "COMPLETED  VERIFIED         objects=320    ABCDEF12",
    )

    try:
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert knowledge.item(0).text() == "Fact · Asserted · R3 · A durable fact"
        assert claim.item(0).text() == (
            "Observation · Supported · R2 · A supported claim"
        )
        assert decision.item(0).text() == (
            "Contradiction · 89.0% · Conflicting values"
        )
        assert research.item(0).text() == "Running · 42.0% · Compare the sources"
        assert jobs.item(0).text() == (
            "Waiting · Priority 5 · Exhaustive Research · Synthesis · Waiting for input"
        )
        assert files.item(0).text() == "Ready · 1.2 MiB · report.pdf"
        assert backups.item(0).text() == "Completed · Verified · 320 objects"

        first_pass = tuple(
            widget.item(0).text()
            for widget in (knowledge, claim, decision, research, jobs, files, backups)
        )
        _sync_dynamic_workspace_copy(window)
        second_pass = tuple(
            widget.item(0).text()
            for widget in (knowledge, claim, decision, research, jobs, files, backups)
        )
        assert second_pass == first_pass
    finally:
        window.close()
        app.processEvents()
