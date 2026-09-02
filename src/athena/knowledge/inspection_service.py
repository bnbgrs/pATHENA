"""Transport-neutral read and decision boundary for canonical Claim state."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from athena.knowledge.models import (
    ClaimEvidenceRef,
    ClaimRevision,
    ClaimSnapshot,
    ProvenanceInputRef,
)
from athena.knowledge.review_service import ReviewError, ReviewItem, ReviewStatus


class ClaimReader(Protocol):
    """Minimal canonical Claim read boundary required by inspection."""

    def load(self, claim_id: uuid.UUID) -> ClaimSnapshot: ...

    def list(self, *, limit: int = 50) -> tuple[ClaimSnapshot, ...]: ...

    def history(self, claim_id: uuid.UUID) -> tuple[ClaimRevision, ...]: ...

    def evidence(self, claim_id: uuid.UUID) -> tuple[ClaimEvidenceRef, ...]: ...

    def provenance_inputs(
        self,
        provenance_id: uuid.UUID,
    ) -> tuple[ProvenanceInputRef, ...]: ...


class ContradictionReviewQueue(Protocol):
    """Minimal persistent contradiction-review boundary required by inspection."""

    def list_pending(
        self,
        *,
        review_type: str | None = None,
        limit: int = 100,
    ) -> tuple[ReviewItem, ...]: ...

    def get(self, review_id: uuid.UUID) -> ReviewItem: ...

    def accept(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> ReviewItem: ...

    def reject(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> ReviewItem: ...


class ContradictionDecision(str, Enum):
    """Explicit user decision for one model-proposed contradiction."""

    CONFIRM = "confirm"
    REJECT = "reject"


class ClaimInspectionError(RuntimeError):
    """Raised when durable Claim/review state is inconsistent or unavailable."""


class ContradictionReviewConflictError(ClaimInspectionError):
    """Raised when a review cannot be resolved from its current durable state."""


def _bounded_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("limit must be an integer between 1 and 500")
    if not 1 <= value <= 500:
        raise ValueError("limit must be between 1 and 500")
    return value


def _require_uuid(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")
    return value


@dataclass(frozen=True, slots=True)
class ClaimDetails:
    """One current Claim plus its durable provenance and evidence graph edges."""

    snapshot: ClaimSnapshot
    provenance_inputs: tuple[ProvenanceInputRef, ...]
    evidence: tuple[ClaimEvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class ContradictionReviewDetails:
    """One review with the exact immutable Claim revisions it was based on."""

    review: ReviewItem
    left_revision: ClaimRevision
    right_revision: ClaimRevision


class KnowledgeInspectionService:
    """Stable application boundary for canonical Claims and contradiction reviews.

    This service deliberately does not expose repositories or SQL rows.  It also
    preserves the review service's fail-closed stale-revision checks: confirming
    a pending contradiction delegates to ``ReviewService.accept`` which requires
    both referenced Claim revisions to still be current.
    """

    def __init__(
        self,
        *,
        claims: ClaimReader,
        reviews: ContradictionReviewQueue,
    ) -> None:
        self._claims = claims
        self._reviews = reviews

    def list_claims(self, *, limit: int = 100) -> tuple[ClaimSnapshot, ...]:
        validated_limit = _bounded_limit(limit)
        return self._claims.list(limit=validated_limit)

    def load_claim(self, claim_id: uuid.UUID) -> ClaimDetails:
        validated_claim_id = _require_uuid(claim_id, "claim_id")
        snapshot = self._claims.load(validated_claim_id)
        return ClaimDetails(
            snapshot=snapshot,
            provenance_inputs=self._claims.provenance_inputs(
                snapshot.revision.provenance_id
            ),
            evidence=self._claims.evidence(validated_claim_id),
        )

    def claim_history(self, claim_id: uuid.UUID) -> tuple[ClaimRevision, ...]:
        return self._claims.history(_require_uuid(claim_id, "claim_id"))

    def list_pending_contradictions(
        self,
        *,
        limit: int = 100,
    ) -> tuple[ContradictionReviewDetails, ...]:
        validated_limit = _bounded_limit(limit)
        try:
            items = self._reviews.list_pending(
                review_type="contradiction",
                limit=validated_limit,
            )
        except ReviewError as exc:
            raise ClaimInspectionError(str(exc)) from exc
        return tuple(self._contradiction_details(item) for item in items)

    def load_contradiction_review(
        self,
        review_id: uuid.UUID,
    ) -> ContradictionReviewDetails:
        validated_review_id = _require_uuid(review_id, "review_id")
        try:
            item = self._reviews.get(validated_review_id)
        except ReviewError as exc:
            raise ClaimInspectionError(str(exc)) from exc
        return self._contradiction_details(item)

    def resolve_contradiction_review(
        self,
        review_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        decision: ContradictionDecision,
    ) -> ContradictionReviewDetails:
        """Resolve a review idempotently while preserving stale-review safety."""
        validated_review_id = _require_uuid(review_id, "review_id")
        validated_actor_id = _require_uuid(actor_id, "actor_id")
        if not isinstance(decision, ContradictionDecision):
            raise TypeError("decision must be a ContradictionDecision.")

        current = self.load_contradiction_review(validated_review_id).review
        if decision is ContradictionDecision.CONFIRM:
            if current.status is ReviewStatus.ACCEPTED:
                return self.load_contradiction_review(validated_review_id)
            if current.status is not ReviewStatus.PENDING:
                raise ContradictionReviewConflictError(
                    "Contradiction review is already resolved with another decision."
                )
            try:
                self._reviews.accept(validated_review_id, actor_id=validated_actor_id)
            except ReviewError as exc:
                raise ContradictionReviewConflictError(str(exc)) from exc
            return self.load_contradiction_review(validated_review_id)

        if current.status is ReviewStatus.REJECTED:
            return self.load_contradiction_review(validated_review_id)
        if current.status is not ReviewStatus.PENDING:
            raise ContradictionReviewConflictError(
                "Contradiction review is already resolved with another decision."
            )
        try:
            self._reviews.reject(validated_review_id, actor_id=validated_actor_id)
        except ReviewError as exc:
            raise ContradictionReviewConflictError(str(exc)) from exc
        return self.load_contradiction_review(validated_review_id)

    def _contradiction_details(
        self,
        item: ReviewItem,
    ) -> ContradictionReviewDetails:
        if item.review_type != "contradiction":
            raise ClaimInspectionError("Review item is not a contradiction review.")
        if (
            item.left_entity_id is None
            or item.left_revision_id is None
            or item.right_entity_id is None
            or item.right_revision_id is None
        ):
            raise ClaimInspectionError(
                "Contradiction review lacks canonical Claim revision references."
            )
        return ContradictionReviewDetails(
            review=item,
            left_revision=self._claim_revision(
                claim_id=item.left_entity_id,
                revision_id=item.left_revision_id,
            ),
            right_revision=self._claim_revision(
                claim_id=item.right_entity_id,
                revision_id=item.right_revision_id,
            ),
        )

    def _claim_revision(
        self,
        *,
        claim_id: uuid.UUID,
        revision_id: uuid.UUID,
    ) -> ClaimRevision:
        revision = next(
            (
                item
                for item in self._claims.history(claim_id)
                if item.revision_id == revision_id
            ),
            None,
        )
        if revision is None:
            raise ClaimInspectionError(
                "Contradiction review references a missing Claim revision."
            )
        return revision
