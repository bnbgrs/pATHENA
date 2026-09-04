from __future__ import annotations

import uuid

import pytest

from athena.knowledge.attribution_contradiction_policy import (
    AttributionContradictionPolicy,
    AttributionContradictionState,
)
from athena.knowledge.models import ClaimDraft, ClaimKind


def _claim(
    *,
    kind: ClaimKind,
    attributed_to: uuid.UUID | None,
) -> ClaimDraft:
    return ClaimDraft(
        claim_kind=kind,
        statement="A source-specific assertion.",
        attributed_to_entity_id=attributed_to,
    )


def test_distinct_attributed_opinions_do_not_become_objective_contradiction_candidates() -> None:
    left_source = uuid.uuid4()
    right_source = uuid.uuid4()

    assessment = AttributionContradictionPolicy.assess(
        _claim(kind=ClaimKind.ATTRIBUTED_OPINION, attributed_to=left_source),
        _claim(kind=ClaimKind.ATTRIBUTED_OPINION, attributed_to=right_source),
    )

    assert assessment.state is AttributionContradictionState.DISTINCT_ATTRIBUTED_OPINIONS
    assert assessment.left_attributed_to_entity_id == left_source
    assert assessment.right_attributed_to_entity_id == right_source
    assert assessment.permits_contradiction_candidate is False


def test_same_attribution_remains_eligible_for_semantic_contradiction_review() -> None:
    source_id = uuid.uuid4()

    assessment = AttributionContradictionPolicy.assess(
        _claim(kind=ClaimKind.ATTRIBUTED_OPINION, attributed_to=source_id),
        _claim(kind=ClaimKind.ATTRIBUTED_OPINION, attributed_to=source_id),
    )

    assert assessment.state is AttributionContradictionState.NOT_DISJOINT
    assert assessment.permits_contradiction_candidate is True


def test_unattributed_attributed_opinion_is_rejected_by_canonical_claim_model() -> None:
    with pytest.raises(ValueError, match="attributed_to_entity_id"):
        _claim(kind=ClaimKind.ATTRIBUTED_OPINION, attributed_to=None)


def test_mixed_or_factual_claims_are_not_suppressed_by_attribution_policy() -> None:
    assessment = AttributionContradictionPolicy.assess(
        _claim(kind=ClaimKind.FACTUAL_ASSERTION, attributed_to=None),
        _claim(kind=ClaimKind.ATTRIBUTED_OPINION, attributed_to=uuid.uuid4()),
    )

    assert assessment.left_attributed_to_entity_id is None
    assert assessment.permits_contradiction_candidate is True


def test_policy_rejects_non_claimdraft_inputs() -> None:
    claim = _claim(kind=ClaimKind.FACTUAL_ASSERTION, attributed_to=None)

    with pytest.raises(TypeError, match="ClaimDraft"):
        AttributionContradictionPolicy.assess(object(), claim)  # type: ignore[arg-type]
