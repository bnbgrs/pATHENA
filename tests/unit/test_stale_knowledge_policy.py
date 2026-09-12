from __future__ import annotations

import pytest

from athena.knowledge.stale_policy import (
    StaleKnowledgePolicy,
    StaleKnowledgeReason,
    StaleKnowledgeState,
)


def test_expired_validity_emits_stale_signal_without_truth_judgment() -> None:
    assessment = StaleKnowledgePolicy.assess(now_us=200, valid_to_us=199)

    assert assessment.state is StaleKnowledgeState.STALE_SIGNAL
    assert assessment.reasons == (StaleKnowledgeReason.VALIDITY_ENDED,)
    assert assessment.requires_revalidation is True


def test_old_source_emits_stale_signal() -> None:
    assessment = StaleKnowledgePolicy.assess(
        now_us=1_000,
        source_observed_at_us=100,
        max_source_age_us=500,
    )

    assert assessment.state is StaleKnowledgeState.STALE_SIGNAL
    assert assessment.reasons == (StaleKnowledgeReason.SOURCE_AGE_EXCEEDED,)


def test_current_or_missing_maintenance_evidence_is_not_marked_stale() -> None:
    current = StaleKnowledgePolicy.assess(
        now_us=1_000,
        valid_to_us=1_000,
        source_observed_at_us=500,
        max_source_age_us=500,
    )
    unknown = StaleKnowledgePolicy.assess(now_us=1_000)

    assert current.state is StaleKnowledgeState.CURRENT_OR_UNKNOWN
    assert current.reasons == ()
    assert unknown.state is StaleKnowledgeState.CURRENT_OR_UNKNOWN
    assert unknown.requires_revalidation is False


def test_multiple_stale_reasons_are_preserved_deterministically() -> None:
    assessment = StaleKnowledgePolicy.assess(
        now_us=1_000,
        valid_to_us=900,
        source_observed_at_us=100,
        max_source_age_us=500,
    )

    assert assessment.reasons == (
        StaleKnowledgeReason.VALIDITY_ENDED,
        StaleKnowledgeReason.SOURCE_AGE_EXCEEDED,
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"now_us": -1}, "now_us"),
        (
            {"now_us": 100, "source_observed_at_us": 10},
            "requires both",
        ),
        (
            {
                "now_us": 100,
                "source_observed_at_us": 101,
                "max_source_age_us": 50,
            },
            "cannot be later",
        ),
        ({"now_us": True}, "now_us"),
    ],
)
def test_invalid_stale_boundaries_fail_closed(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        StaleKnowledgePolicy.assess(**kwargs)  # type: ignore[arg-type]
