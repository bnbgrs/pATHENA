from __future__ import annotations

import uuid

from athena.knowledge.contradiction_policy import TemporalContradictionState
from athena.knowledge.contradiction_review_gate import (
    assess_canonical_contradiction_candidate,
)
from athena.knowledge.models import ClaimDraft, ClaimKind


def _claim(
    *,
    kind: ClaimKind = ClaimKind.FACTUAL_ASSERTION,
    attributed_to: uuid.UUID | None = None,
    valid_from_us: int | None = None,
    valid_to_us: int | None = None,
) -> ClaimDraft:
    return ClaimDraft(
        claim_kind=kind,
        statement="A canonical assertion.",
        attributed_to_entity_id=attributed_to,
        valid_from_us=valid_from_us,
        valid_to_us=valid_to_us,
    )


def test_combined_gate_uses_same_exact_revision_pair_for_both_policies(monkeypatch) -> None:
    from athena.knowledge import contradiction_review_gate as gate

    left_revision_id = uuid.uuid4()
    right_revision_id = uuid.uuid4()
    left = _claim(valid_from_us=0, valid_to_us=100)
    right = _claim(valid_from_us=50, valid_to_us=150)
    loaded: list[uuid.UUID] = []

    def fake_load_claim_draft(connection: object, *, revision_id: uuid.UUID) -> ClaimDraft:
        loaded.append(revision_id)
        return left if revision_id == left_revision_id else right

    monkeypatch.setattr(gate, "_load_claim_draft", fake_load_claim_draft)

    assessment = assess_canonical_contradiction_candidate(
        object(),  # type: ignore[arg-type]
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )

    assert loaded == [left_revision_id, right_revision_id]
    assert assessment.temporal.state is TemporalContradictionState.OVERLAPPING_OR_UNKNOWN
    assert assessment.temporal.permits_contradiction_candidate is True
    assert assessment.attribution.permits_contradiction_candidate is True
    assert assessment.permits_contradiction_candidate is True


def test_combined_gate_rejects_temporally_disjoint_pair(monkeypatch) -> None:
    from athena.knowledge import contradiction_review_gate as gate

    left_revision_id = uuid.uuid4()
    right_revision_id = uuid.uuid4()
    claims = {
        left_revision_id: _claim(valid_from_us=0, valid_to_us=10),
        right_revision_id: _claim(valid_from_us=20, valid_to_us=30),
    }
    monkeypatch.setattr(
        gate,
        "_load_claim_draft",
        lambda connection, *, revision_id: claims[revision_id],
    )

    assessment = assess_canonical_contradiction_candidate(
        object(),  # type: ignore[arg-type]
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )

    assert assessment.temporal.state is TemporalContradictionState.DISJOINT
    assert assessment.attribution.permits_contradiction_candidate is True
    assert assessment.permits_contradiction_candidate is False


def test_combined_gate_rejects_distinct_attributed_opinions(monkeypatch) -> None:
    from athena.knowledge import contradiction_review_gate as gate

    left_revision_id = uuid.uuid4()
    right_revision_id = uuid.uuid4()
    claims = {
        left_revision_id: _claim(
            kind=ClaimKind.ATTRIBUTED_OPINION,
            attributed_to=uuid.uuid4(),
        ),
        right_revision_id: _claim(
            kind=ClaimKind.ATTRIBUTED_OPINION,
            attributed_to=uuid.uuid4(),
        ),
    }
    monkeypatch.setattr(
        gate,
        "_load_claim_draft",
        lambda connection, *, revision_id: claims[revision_id],
    )

    assessment = assess_canonical_contradiction_candidate(
        object(),  # type: ignore[arg-type]
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )

    assert assessment.temporal.permits_contradiction_candidate is True
    assert assessment.attribution.permits_contradiction_candidate is False
    assert assessment.permits_contradiction_candidate is False
