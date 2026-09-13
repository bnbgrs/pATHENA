from __future__ import annotations

import uuid
from typing import cast

import pytest

from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
)
from athena.knowledge.stale_policy import (
    StaleKnowledgePolicy,
    StaleKnowledgeReason,
    StaleKnowledgeState,
)
from athena.knowledge.staleness_policy import KnowledgeStalenessPolicy

KNOWLEDGE_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
REVISION_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
ACTOR_ID = uuid.UUID("33333333-3333-4333-8333-333333333333")
PROVENANCE_ID = uuid.UUID("44444444-4444-4444-8444-444444444444")


def _revision(*, valid_to_us: int | None = None) -> KnowledgeUnitRevision:
    return KnowledgeUnitRevision(
        knowledge_id=KNOWLEDGE_ID,
        revision_id=REVISION_ID,
        revision_no=1,
        created_at_us=10,
        created_by_actor_id=ACTOR_ID,
        provenance_id=PROVENANCE_ID,
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            title="Compatibility fact",
            body="Recorded canonical knowledge.",
            valid_to_us=valid_to_us,
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )


@pytest.mark.parametrize(
    (
        "now_us",
        "valid_to_us",
        "source_observed_at_us",
        "max_source_age_us",
        "expected_state",
        "expected_reasons",
    ),
    [
        (100, None, None, None, StaleKnowledgeState.CURRENT_OR_UNKNOWN, ()),
        (
            100,
            99,
            None,
            None,
            StaleKnowledgeState.STALE_SIGNAL,
            (StaleKnowledgeReason.VALIDITY_ENDED,),
        ),
        (
            100,
            None,
            10,
            50,
            StaleKnowledgeState.STALE_SIGNAL,
            (StaleKnowledgeReason.SOURCE_AGE_EXCEEDED,),
        ),
        (
            100,
            99,
            10,
            50,
            StaleKnowledgeState.STALE_SIGNAL,
            (
                StaleKnowledgeReason.VALIDITY_ENDED,
                StaleKnowledgeReason.SOURCE_AGE_EXCEEDED,
            ),
        ),
        (100, 100, 50, 50, StaleKnowledgeState.CURRENT_OR_UNKNOWN, ()),
    ],
)
def test_legacy_policy_uses_canonical_temporal_decisions(
    now_us: int,
    valid_to_us: int | None,
    source_observed_at_us: int | None,
    max_source_age_us: int | None,
    expected_state: StaleKnowledgeState,
    expected_reasons: tuple[StaleKnowledgeReason, ...],
) -> None:
    legacy = StaleKnowledgePolicy.assess(
        now_us=now_us,
        valid_to_us=valid_to_us,
        source_observed_at_us=source_observed_at_us,
        max_source_age_us=max_source_age_us,
    )
    canonical = KnowledgeStalenessPolicy.assess(
        _revision(valid_to_us=valid_to_us),
        assessed_at_us=now_us,
        source_observed_at_us=source_observed_at_us,
        max_source_age_us=max_source_age_us,
    )

    assert legacy.state is expected_state
    assert legacy.reasons == expected_reasons
    assert tuple(reason.value for reason in legacy.reasons) == tuple(
        reason.value for reason in canonical.reasons
    )
    assert legacy.requires_revalidation is canonical.should_signal_stale


def test_legacy_policy_preserves_unknown_without_inventing_freshness() -> None:
    legacy = StaleKnowledgePolicy.assess(now_us=100)
    canonical = KnowledgeStalenessPolicy.assess(_revision(), assessed_at_us=100)

    assert legacy.state is StaleKnowledgeState.CURRENT_OR_UNKNOWN
    assert legacy.reasons == ()
    assert legacy.requires_revalidation is False
    assert canonical.should_signal_stale is False


@pytest.mark.parametrize("now_us", [True, -1, 1.5, "100"])
def test_legacy_policy_preserves_fail_closed_value_contract(now_us: object) -> None:
    with pytest.raises(ValueError, match="now_us must be a non-negative integer"):
        StaleKnowledgePolicy.assess(now_us=cast(int, now_us))


def test_both_policy_surfaces_reject_future_source_observation() -> None:
    with pytest.raises(ValueError, match="cannot be later than now_us"):
        StaleKnowledgePolicy.assess(
            now_us=100,
            source_observed_at_us=101,
            max_source_age_us=10,
        )
    with pytest.raises(ValueError, match="must not be in the future"):
        KnowledgeStalenessPolicy.assess(
            _revision(),
            assessed_at_us=100,
            source_observed_at_us=101,
            max_source_age_us=10,
        )
