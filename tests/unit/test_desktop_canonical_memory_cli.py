from __future__ import annotations

import argparse
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.desktop.canonical_memory_cli import _run
from athena.knowledge.extraction_models import ProposalEntityType
from athena.knowledge.models import ClaimKind
from athena.knowledge.review_service import (
    MergeReviewDetails,
    ReviewItem,
    ReviewStatus,
)


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def test_claim_relations_show_reciprocal_canonical_contradiction(
    tmp_path: Path,
    capsys,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        chat_id = app.chat.create_chat()
        left_message = app.chat.add_user_message(
            chat_id=chat_id,
            content="The archive is open on Sundays.",
        )
        right_message = app.chat.add_user_message(
            chat_id=chat_id,
            content="The archive is closed on Sundays.",
        )
        left = app.claims.promote_chat_message(
            chat_id=chat_id,
            sequence_no=left_message.sequence_no,
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
        )
        right = app.claims.promote_chat_message(
            chat_id=chat_id,
            sequence_no=right_message.sequence_no,
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
        )
        app.claims.mark_contradiction(
            left_claim_id=left.claim_id,
            right_claim_id=right.claim_id,
        )

        assert _run(
            app,
            argparse.Namespace(command="claim-relations", claim_id=left.claim_id),
        ) == 0
        output = capsys.readouterr().out
        assert f"CLAIM {left.claim_id}" in output
        assert "RELATION_COUNT" in output
        assert f"RELATION\toriginates\t{left_message.message_id}" in output
        assert "\tmessage\t-\t-\tChat-message provenance source" in output
        assert "RELATION\tcontradicts\t" in output
        assert str(right.claim_id) in output
        assert "The archive is closed on Sundays." in output
    finally:
        app.stop()


class _FakeReviews:
    def __init__(self) -> None:
        self.review_id = uuid.uuid4()
        self.target_id = uuid.uuid4()
        self.target_revision_id = uuid.uuid4()
        self.run_id = uuid.uuid4()
        self.model_id = uuid.uuid4()
        self.source_id = uuid.uuid4()
        self.source_revision_id = uuid.uuid4()
        self.decisions: list[str] = []
        self.item = ReviewItem(
            review_id=self.review_id,
            review_type="merge_candidate",
            status=ReviewStatus.PENDING,
            created_at_us=1,
            resolved_at_us=None,
            processing_run_id=self.run_id,
            model_signature_id=self.model_id,
            left_entity_id=self.target_id,
            left_revision_id=self.target_revision_id,
            right_entity_id=None,
            right_revision_id=None,
            confidence=0.91,
            reason="near duplicate",
            decision_actor_id=None,
            decision_reason=None,
        )
        self.details = MergeReviewDetails(
            review_id=self.review_id,
            proposal_type=ProposalEntityType.KNOWLEDGE,
            proposal_index=2,
            source_entity_id=self.source_id,
            source_revision_id=self.source_revision_id,
            proposal_text="Candidate semantic text",
            proposal_kind="idea",
            proposal_epistemic_status="asserted",
            similarity=0.91,
            decision=None,
            existing_entity_id=self.target_id,
            existing_revision_id=self.target_revision_id,
        )

    def list_pending(self, *, review_type: str | None = None, limit: int = 100):
        assert review_type == "merge_candidate"
        assert limit == 20
        return (self.item,)

    def merge_details(self, review_id: uuid.UUID) -> MergeReviewDetails:
        assert review_id == self.review_id
        return self.details

    def resolve_merge(
        self,
        review_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        decision: str,
    ) -> ReviewItem:
        assert review_id == self.review_id
        assert isinstance(actor_id, uuid.UUID)
        self.decisions.append(decision)
        return ReviewItem(
            review_id=self.item.review_id,
            review_type=self.item.review_type,
            status=ReviewStatus.ACCEPTED,
            created_at_us=self.item.created_at_us,
            resolved_at_us=2,
            processing_run_id=self.item.processing_run_id,
            model_signature_id=self.item.model_signature_id,
            left_entity_id=self.item.left_entity_id,
            left_revision_id=self.item.left_revision_id,
            right_entity_id=None,
            right_revision_id=None,
            confidence=self.item.confidence,
            reason=self.item.reason,
            decision_actor_id=actor_id,
            decision_reason=decision,
        )


def test_merge_list_and_explicit_decisions_use_review_service(capsys) -> None:
    reviews = _FakeReviews()
    actor_id = uuid.uuid4()
    app = SimpleNamespace(
        reviews=reviews,
        chat=SimpleNamespace(ensure_local_user=lambda: actor_id),
    )
    typed_app = cast(Any, app)

    assert _run(typed_app, argparse.Namespace(command="merge-list", limit=20)) == 0
    listing = capsys.readouterr().out
    assert str(reviews.review_id) in listing
    assert "knowledge\t2\t0.910000" in listing
    assert "Candidate semantic text" in listing

    assert _run(
        typed_app,
        argparse.Namespace(command="merge", review_id=reviews.review_id),
    ) == 0
    merged = capsys.readouterr().out
    assert "MERGE_REVIEW_RESOLVED" in merged
    assert reviews.decisions == ["merge"]

    assert _run(
        typed_app,
        argparse.Namespace(command="keep-separate", review_id=reviews.review_id),
    ) == 0
    separated = capsys.readouterr().out
    assert "MERGE_REVIEW_RESOLVED" in separated
    assert reviews.decisions == ["merge", "keep_separate"]
