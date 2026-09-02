from __future__ import annotations

import uuid

import pytest

from athena.knowledge.inspection_service import (
    ClaimInspectionError,
    ContradictionDecision,
    ContradictionReviewConflictError,
    KnowledgeInspectionService,
)
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
from athena.knowledge.review_service import ReviewError, ReviewItem, ReviewStatus


def _revision(
    claim_id: uuid.UUID,
    *,
    revision_no: int,
    statement: str,
) -> ClaimRevision:
    return ClaimRevision(
        claim_id=claim_id,
        revision_id=uuid.uuid4(),
        revision_no=revision_no,
        created_at_us=revision_no,
        created_by_actor_id=uuid.uuid4(),
        provenance_id=uuid.uuid4(),
        payload=ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement=statement,
            epistemic_status=EpistemicStatus.ASSERTED,
        ),
    )


class _Claims:
    def __init__(self, revisions: dict[uuid.UUID, tuple[ClaimRevision, ...]]) -> None:
        self.revisions = revisions
        self.evidence_by_claim: dict[uuid.UUID, tuple[ClaimEvidenceRef, ...]] = {}
        self.provenance_by_id: dict[uuid.UUID, tuple[ProvenanceInputRef, ...]] = {}

    def load(self, claim_id: uuid.UUID) -> ClaimSnapshot:
        revision = self.revisions[claim_id][-1]
        return ClaimSnapshot(
            claim_id=claim_id,
            lifecycle_state="active",
            revision=revision,
        )

    def list(self, *, limit: int = 50) -> tuple[ClaimSnapshot, ...]:
        return tuple(self.load(claim_id) for claim_id in self.revisions)[:limit]

    def history(self, claim_id: uuid.UUID) -> tuple[ClaimRevision, ...]:
        return self.revisions[claim_id]

    def evidence(self, claim_id: uuid.UUID) -> tuple[ClaimEvidenceRef, ...]:
        return self.evidence_by_claim.get(claim_id, ())

    def provenance_inputs(
        self,
        provenance_id: uuid.UUID,
    ) -> tuple[ProvenanceInputRef, ...]:
        return self.provenance_by_id.get(provenance_id, ())


class _Reviews:
    def __init__(self, items: tuple[ReviewItem, ...]) -> None:
        self.items = {item.review_id: item for item in items}
        self.accept_calls = 0
        self.reject_calls = 0
        self.accept_error: ReviewError | None = None
        self.reject_error: ReviewError | None = None

    def list_pending(
        self,
        *,
        review_type: str | None = None,
        limit: int = 100,
    ) -> tuple[ReviewItem, ...]:
        items = tuple(
            item
            for item in self.items.values()
            if item.status is ReviewStatus.PENDING
            and (review_type is None or item.review_type == review_type)
        )
        return items[:limit]

    def get(self, review_id: uuid.UUID) -> ReviewItem:
        try:
            return self.items[review_id]
        except KeyError as exc:
            raise ReviewError(f"Review item not found: {review_id}") from exc

    def accept(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> ReviewItem:
        del actor_id
        self.accept_calls += 1
        if self.accept_error is not None:
            raise self.accept_error
        item = self.get(review_id)
        if item.status is not ReviewStatus.PENDING:
            raise ReviewError("Review item is no longer pending.")
        resolved = _with_status(item, ReviewStatus.ACCEPTED)
        self.items[review_id] = resolved
        return resolved

    def reject(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> ReviewItem:
        del actor_id
        self.reject_calls += 1
        if self.reject_error is not None:
            raise self.reject_error
        item = self.get(review_id)
        if item.status is not ReviewStatus.PENDING:
            raise ReviewError("Review item is no longer pending.")
        resolved = _with_status(item, ReviewStatus.REJECTED)
        self.items[review_id] = resolved
        return resolved


def _with_status(item: ReviewItem, status: ReviewStatus) -> ReviewItem:
    return ReviewItem(
        review_id=item.review_id,
        review_type=item.review_type,
        status=status,
        created_at_us=item.created_at_us,
        resolved_at_us=(None if status is ReviewStatus.PENDING else 2),
        processing_run_id=item.processing_run_id,
        model_signature_id=item.model_signature_id,
        left_entity_id=item.left_entity_id,
        left_revision_id=item.left_revision_id,
        right_entity_id=item.right_entity_id,
        right_revision_id=item.right_revision_id,
        confidence=item.confidence,
        reason=item.reason,
        decision_actor_id=item.decision_actor_id,
        decision_reason=item.decision_reason,
    )


def _review(
    *,
    left: ClaimRevision,
    right: ClaimRevision,
    status: ReviewStatus = ReviewStatus.PENDING,
    review_type: str = "contradiction",
) -> ReviewItem:
    return ReviewItem(
        review_id=uuid.uuid4(),
        review_type=review_type,
        status=status,
        created_at_us=1,
        resolved_at_us=None,
        processing_run_id=uuid.uuid4(),
        model_signature_id=uuid.uuid4(),
        left_entity_id=left.claim_id,
        left_revision_id=left.revision_id,
        right_entity_id=right.claim_id,
        right_revision_id=right.revision_id,
        confidence=0.91,
        reason="model detected a semantic contradiction",
        decision_actor_id=None,
        decision_reason=None,
    )


def test_load_claim_includes_current_revision_provenance_and_evidence() -> None:
    claim_id = uuid.uuid4()
    revision = _revision(claim_id, revision_no=1, statement="Alpha")
    claims = _Claims({claim_id: (revision,)})
    provenance = ProvenanceInputRef(
        provenance_id=revision.provenance_id,
        input_entity_id=uuid.uuid4(),
        input_revision_id=uuid.uuid4(),
        input_role="chat_message_source",
        ordinal=0,
    )
    evidence = ClaimEvidenceRef(
        evidence_role=EvidenceRole.ORIGINATES,
        provenance_id=revision.provenance_id,
        message_id=uuid.uuid4(),
    )
    claims.provenance_by_id[revision.provenance_id] = (provenance,)
    claims.evidence_by_claim[claim_id] = (evidence,)

    service = KnowledgeInspectionService(claims=claims, reviews=_Reviews(()))
    details = service.load_claim(claim_id)

    assert details.snapshot.revision == revision
    assert details.provenance_inputs == (provenance,)
    assert details.evidence == (evidence,)


def test_pending_contradiction_uses_exact_frozen_historical_revisions() -> None:
    left_id = uuid.uuid4()
    right_id = uuid.uuid4()
    left_v1 = _revision(left_id, revision_no=1, statement="Left v1")
    left_v2 = _revision(left_id, revision_no=2, statement="Left v2")
    right_v1 = _revision(right_id, revision_no=1, statement="Right v1")
    review = _review(left=left_v1, right=right_v1)
    service = KnowledgeInspectionService(
        claims=_Claims({left_id: (left_v1, left_v2), right_id: (right_v1,)}),
        reviews=_Reviews((review,)),
    )

    details = service.list_pending_contradictions()

    assert len(details) == 1
    assert details[0].left_revision == left_v1
    assert details[0].right_revision == right_v1


def test_confirm_contradiction_is_idempotent_after_success() -> None:
    left = _revision(uuid.uuid4(), revision_no=1, statement="Left")
    right = _revision(uuid.uuid4(), revision_no=1, statement="Right")
    review = _review(left=left, right=right)
    reviews = _Reviews((review,))
    service = KnowledgeInspectionService(
        claims=_Claims({left.claim_id: (left,), right.claim_id: (right,)}),
        reviews=reviews,
    )
    actor_id = uuid.uuid4()

    first = service.resolve_contradiction_review(
        review.review_id,
        actor_id=actor_id,
        decision=ContradictionDecision.CONFIRM,
    )
    second = service.resolve_contradiction_review(
        review.review_id,
        actor_id=actor_id,
        decision=ContradictionDecision.CONFIRM,
    )

    assert first.review.status is ReviewStatus.ACCEPTED
    assert second.review.status is ReviewStatus.ACCEPTED
    assert reviews.accept_calls == 1


def test_opposite_decision_after_resolution_fails_closed() -> None:
    left = _revision(uuid.uuid4(), revision_no=1, statement="Left")
    right = _revision(uuid.uuid4(), revision_no=1, statement="Right")
    review = _review(left=left, right=right, status=ReviewStatus.ACCEPTED)
    service = KnowledgeInspectionService(
        claims=_Claims({left.claim_id: (left,), right.claim_id: (right,)}),
        reviews=_Reviews((review,)),
    )

    with pytest.raises(ContradictionReviewConflictError):
        service.resolve_contradiction_review(
            review.review_id,
            actor_id=uuid.uuid4(),
            decision=ContradictionDecision.REJECT,
        )


def test_stale_revision_error_from_review_transaction_is_preserved_as_conflict() -> None:
    left = _revision(uuid.uuid4(), revision_no=1, statement="Left")
    right = _revision(uuid.uuid4(), revision_no=1, statement="Right")
    review = _review(left=left, right=right)
    reviews = _Reviews((review,))
    reviews.accept_error = ReviewError(
        "Canonical Claim changed since review was queued; re-extraction is required."
    )
    service = KnowledgeInspectionService(
        claims=_Claims({left.claim_id: (left,), right.claim_id: (right,)}),
        reviews=reviews,
    )

    with pytest.raises(ContradictionReviewConflictError, match="changed since review"):
        service.resolve_contradiction_review(
            review.review_id,
            actor_id=uuid.uuid4(),
            decision=ContradictionDecision.CONFIRM,
        )

    assert reviews.get(review.review_id).status is ReviewStatus.PENDING
    assert reviews.accept_calls == 1


def test_non_contradiction_review_is_rejected_by_inspection_boundary() -> None:
    left = _revision(uuid.uuid4(), revision_no=1, statement="Left")
    right = _revision(uuid.uuid4(), revision_no=1, statement="Right")
    review = _review(left=left, right=right, review_type="merge_candidate")
    service = KnowledgeInspectionService(
        claims=_Claims({left.claim_id: (left,), right.claim_id: (right,)}),
        reviews=_Reviews((review,)),
    )

    with pytest.raises(ClaimInspectionError, match="not a contradiction"):
        service.load_contradiction_review(review.review_id)
