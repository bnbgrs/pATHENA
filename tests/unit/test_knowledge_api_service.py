from __future__ import annotations

import uuid

import pytest

from athena.api.knowledge import KnowledgeApiService
from athena.knowledge.inspection_service import KnowledgeInspectionService
from athena.knowledge.models import (
    ClaimDraft,
    ClaimEvidenceRef,
    ClaimKind,
    ClaimRevision,
    ClaimSnapshot,
    EpistemicStatus,
    EvidenceRole,
    ProvenanceInputRef,
)
from athena.knowledge.review_service import ReviewItem, ReviewStatus


def _revision(claim_id: uuid.UUID, *, statement: str) -> ClaimRevision:
    return ClaimRevision(
        claim_id=claim_id,
        revision_id=uuid.uuid4(),
        revision_no=1,
        created_at_us=123,
        created_by_actor_id=uuid.uuid4(),
        provenance_id=uuid.uuid4(),
        payload=ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement=statement,
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )


class _Claims:
    def __init__(self, left: ClaimRevision, right: ClaimRevision) -> None:
        self._revisions = {
            left.claim_id: (left,),
            right.claim_id: (right,),
        }
        self._provenance = ProvenanceInputRef(
            provenance_id=left.provenance_id,
            input_entity_id=uuid.uuid4(),
            input_revision_id=uuid.uuid4(),
            input_role="chat_message_source",
            ordinal=0,
        )
        self._evidence = ClaimEvidenceRef(
            evidence_role=EvidenceRole.ORIGINATES,
            provenance_id=left.provenance_id,
            message_id=uuid.uuid4(),
        )

    def load(self, claim_id: uuid.UUID) -> ClaimSnapshot:
        revision = self._revisions[claim_id][-1]
        return ClaimSnapshot(
            claim_id=claim_id,
            lifecycle_state="active",
            revision=revision,
        )

    def list(self, *, limit: int = 50) -> tuple[ClaimSnapshot, ...]:
        return tuple(self.load(claim_id) for claim_id in self._revisions)[:limit]

    def history(self, claim_id: uuid.UUID) -> tuple[ClaimRevision, ...]:
        return self._revisions[claim_id]

    def evidence(self, claim_id: uuid.UUID) -> tuple[ClaimEvidenceRef, ...]:
        first_claim_id = next(iter(self._revisions))
        return (self._evidence,) if claim_id == first_claim_id else ()

    def provenance_inputs(
        self,
        provenance_id: uuid.UUID,
    ) -> tuple[ProvenanceInputRef, ...]:
        return (self._provenance,) if provenance_id == self._provenance.provenance_id else ()


class _Reviews:
    def __init__(self, review: ReviewItem) -> None:
        self.review = review

    def list_pending(
        self,
        *,
        review_type: str | None = None,
        limit: int = 100,
    ) -> tuple[ReviewItem, ...]:
        if (
            self.review.status is ReviewStatus.PENDING
            and (review_type is None or review_type == self.review.review_type)
            and limit > 0
        ):
            return (self.review,)
        return ()

    def get(self, review_id: uuid.UUID) -> ReviewItem:
        assert review_id == self.review.review_id
        return self.review

    def accept(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> ReviewItem:
        assert review_id == self.review.review_id
        self.review = _resolved(self.review, ReviewStatus.ACCEPTED, actor_id)
        return self.review

    def reject(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> ReviewItem:
        assert review_id == self.review.review_id
        self.review = _resolved(self.review, ReviewStatus.REJECTED, actor_id)
        return self.review


class _Actors:
    def __init__(self) -> None:
        self.actor_id = uuid.uuid4()
        self.calls = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.calls += 1
        return self.actor_id


def _resolved(
    item: ReviewItem,
    status: ReviewStatus,
    actor_id: uuid.UUID,
) -> ReviewItem:
    return ReviewItem(
        review_id=item.review_id,
        review_type=item.review_type,
        status=status,
        created_at_us=item.created_at_us,
        resolved_at_us=456,
        processing_run_id=item.processing_run_id,
        model_signature_id=item.model_signature_id,
        left_entity_id=item.left_entity_id,
        left_revision_id=item.left_revision_id,
        right_entity_id=item.right_entity_id,
        right_revision_id=item.right_revision_id,
        confidence=item.confidence,
        reason=item.reason,
        decision_actor_id=actor_id,
        decision_reason=(
            "explicit user review acceptance"
            if status is ReviewStatus.ACCEPTED
            else "explicit user review rejection"
        ),
    )


def _api() -> tuple[
    KnowledgeApiService,
    ClaimRevision,
    ClaimRevision,
    ReviewItem,
    _Actors,
]:
    left = _revision(uuid.uuid4(), statement="The system is online.")
    right = _revision(uuid.uuid4(), statement="The system is offline.")
    review = ReviewItem(
        review_id=uuid.uuid4(),
        review_type="contradiction",
        status=ReviewStatus.PENDING,
        created_at_us=100,
        resolved_at_us=None,
        processing_run_id=uuid.uuid4(),
        model_signature_id=uuid.uuid4(),
        left_entity_id=left.claim_id,
        left_revision_id=left.revision_id,
        right_entity_id=right.claim_id,
        right_revision_id=right.revision_id,
        confidence=0.95,
        reason="opposite asserted states",
        decision_actor_id=None,
        decision_reason=None,
    )
    claims = _Claims(left, right)
    reviews = _Reviews(review)
    actors = _Actors()
    inspection = KnowledgeInspectionService(claims=claims, reviews=reviews)
    return (
        KnowledgeApiService(inspection=inspection, actors=actors),
        left,
        right,
        review,
        actors,
    )


def test_claim_response_is_json_safe_and_contains_provenance_and_evidence() -> None:
    api, left, _right, _review, _actors = _api()

    response = api.load_claim(str(left.claim_id))
    payload = response.to_dict()

    assert payload["claim_id"] == str(left.claim_id)
    assert payload["revision"]["revision_id"] == str(left.revision_id)  # type: ignore[index]
    assert payload["revision"]["statement"] == "The system is online."  # type: ignore[index]
    assert payload["provenance_inputs"][0]["input_role"] == "chat_message_source"  # type: ignore[index]
    assert payload["evidence"][0]["evidence_role"] == "originates"  # type: ignore[index]


def test_pending_review_exposes_exact_claim_revisions() -> None:
    api, left, right, review, _actors = _api()

    items = api.list_pending_contradictions()

    assert len(items) == 1
    assert items[0].review_id == str(review.review_id)
    assert items[0].left_revision.revision_id == str(left.revision_id)
    assert items[0].right_revision.revision_id == str(right.revision_id)
    assert items[0].status == "pending"


def test_resolve_review_uses_local_actor_and_returns_durable_decision() -> None:
    api, _left, _right, review, actors = _api()

    resolved = api.resolve_contradiction_review(
        str(review.review_id),
        decision="confirm",
    )

    assert resolved.status == "accepted"
    assert resolved.decision_actor_id == str(actors.actor_id)
    assert actors.calls == 1


def test_invalid_contradiction_decision_is_rejected_before_actor_lookup() -> None:
    api, _left, _right, review, actors = _api()

    with pytest.raises(ValueError, match="confirm.*reject"):
        api.resolve_contradiction_review(
            str(review.review_id),
            decision="merge",
        )

    assert actors.calls == 0
