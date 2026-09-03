from __future__ import annotations

from athena.knowledge.contradiction_policy import (
    TemporalContradictionPolicy,
    TemporalContradictionState,
)
from athena.knowledge.models import ClaimDraft, ClaimKind


def _claim(*, valid_from_us: int | None, valid_to_us: int | None) -> ClaimDraft:
    return ClaimDraft(
        claim_kind=ClaimKind.FACTUAL_ASSERTION,
        statement="A works at an organization.",
        valid_from_us=valid_from_us,
        valid_to_us=valid_to_us,
    )


def test_non_overlapping_claim_windows_are_not_temporal_contradiction_candidates() -> None:
    left = _claim(valid_from_us=2024, valid_to_us=2024)
    right = _claim(valid_from_us=2026, valid_to_us=2026)

    assessment = TemporalContradictionPolicy.assess(left, right)

    assert assessment.state is TemporalContradictionState.DISJOINT
    assert assessment.permits_contradiction_candidate is False


def test_touching_claim_windows_are_not_proven_disjoint() -> None:
    left = _claim(valid_from_us=2024, valid_to_us=2025)
    right = _claim(valid_from_us=2025, valid_to_us=2026)

    assessment = TemporalContradictionPolicy.assess(left, right)

    assert assessment.state is TemporalContradictionState.OVERLAPPING_OR_UNKNOWN
    assert assessment.permits_contradiction_candidate is True


def test_unknown_bounds_do_not_suppress_possible_contradiction() -> None:
    left = _claim(valid_from_us=None, valid_to_us=2025)
    right = _claim(valid_from_us=None, valid_to_us=None)

    assessment = TemporalContradictionPolicy.assess(left, right)

    assert assessment.state is TemporalContradictionState.OVERLAPPING_OR_UNKNOWN
    assert assessment.permits_contradiction_candidate is True


def test_disjoint_open_ended_windows_are_detected_in_both_directions() -> None:
    earlier = _claim(valid_from_us=None, valid_to_us=10)
    later = _claim(valid_from_us=11, valid_to_us=None)

    assert TemporalContradictionPolicy.assess(
        earlier, later
    ).state is TemporalContradictionState.DISJOINT
    assert TemporalContradictionPolicy.assess(
        later, earlier
    ).state is TemporalContradictionState.DISJOINT


def test_policy_rejects_non_claim_inputs() -> None:
    claim = _claim(valid_from_us=None, valid_to_us=None)

    try:
        TemporalContradictionPolicy.assess(claim, object())  # type: ignore[arg-type]
    except TypeError as exc:
        assert "ClaimDraft" in str(exc)
    else:
        raise AssertionError("non-ClaimDraft inputs must be rejected")
