from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.knowledge_review import (
    KnowledgeReviewError,
    parse_knowledge_entity_review,
    render_knowledge_entity_review,
)
from athena.desktop.knowledge_workspace import KnowledgeWorkspace


def _app() -> QApplication:
    return create_application(["pathena-knowledge-review-test"])


def _claim_output() -> str:
    return """CLAIM 11111111-1111-1111-1111-111111111111
LIFECYCLE active
REVISION 2 22222222-2222-2222-2222-222222222222
CREATED_AT_US 42
KIND factual_assertion
STATUS supported
SUBJECT -
PREDICATE retains
OBJECT -
ATTRIBUTED_TO -
VALID_FROM_US -
VALID_TO_US -
STATEMENT
Local memory retains durable evidence.
PROVENANCE_INPUTS 1
PROVENANCE 0 role=source entity=33333333-3333-3333-3333-333333333333 revision=-
EVIDENCE 1
EVIDENCE_REF role=supports anchor=44444444-4444-4444-4444-444444444444 message=- entity=- revision=- provenance=55555555-5555-5555-5555-555555555555
"""


def test_claim_detail_preserves_evidence_and_provenance() -> None:
    review = parse_knowledge_entity_review(_claim_output())
    rendered = render_knowledge_entity_review(review)

    assert review.entity_type == "claim"
    assert review.provenance[0].entity_id.startswith("33333333")
    assert review.evidence[0].anchor_id is not None
    assert "Local memory retains durable evidence." in rendered
    assert "Factual Assertion · Supported · Active" in rendered
    assert "supports · 44444444" in rendered
    assert "Claim 11111111 · Revision 2 22222222" in rendered


def test_knowledge_detail_preserves_multiline_body_and_empty_provenance() -> None:
    output = """KNOWLEDGE aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
LIFECYCLE active
REVISION 1 bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
CREATED_AT_US 7
KIND decision
STATUS accepted
TITLE Retention policy
VALID_FROM_US -
VALID_TO_US -
BODY
Keep durable context.
Delete transient traces.
PROVENANCE_INPUTS 0
"""
    review = parse_knowledge_entity_review(output)

    assert review.content == "Keep durable context.\nDelete transient traces."
    assert "No provenance inputs were persisted" in render_knowledge_entity_review(review)


def test_mismatched_provenance_count_fails_closed() -> None:
    with pytest.raises(KnowledgeReviewError, match="count does not match"):
        parse_knowledge_entity_review(_claim_output().replace("PROVENANCE_INPUTS 1", "PROVENANCE_INPUTS 2"))


def test_workspace_renders_verified_claim_and_marks_state() -> None:
    app = _app()
    workspace = KnowledgeWorkspace(object(), None)
    workspace._knowledge_refresh_timer.stop()
    workspace.browser_tabs.setCurrentIndex(3)
    app.processEvents()
    try:
        workspace._knowledge_operation = "claim-show"
        workspace._knowledge_buffer = _claim_output()
        workspace._knowledge_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.claim_details.property("pathenaKnowledgeReviewState") == "ready"
        assert workspace.claim_details.property("pathenaKnowledgeEntityId") == (
            "11111111-1111-1111-1111-111111111111"
        )
        assert workspace.claim_details.toPlainText().startswith("CLAIM\n")
    finally:
        workspace.close()
        app.processEvents()


def test_workspace_keeps_raw_output_when_detail_is_unreadable() -> None:
    app = _app()
    workspace = KnowledgeWorkspace(object(), None)
    workspace._knowledge_refresh_timer.stop()
    workspace.browser_tabs.setCurrentIndex(3)
    app.processEvents()
    try:
        workspace._knowledge_operation = "show"
        workspace._knowledge_buffer = "not-a-persisted-detail"
        workspace._knowledge_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.knowledge_details.property("pathenaKnowledgeReviewState") == "error"
        assert "Raw command output:\nnot-a-persisted-detail" in workspace.knowledge_details.toPlainText()
    finally:
        workspace.close()
        app.processEvents()
