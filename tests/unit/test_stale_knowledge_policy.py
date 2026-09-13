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
from athena.knowledge.staleness_policy import (
    KnowledgeStalenessPolicy,
    KnowledgeStalenessReason,
    KnowledgeStalenessState,
)

KNOWLEDGE_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
REVISION_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
ACTOR_ID = uuid.UUID("33333333-3333-4333-8333-333333333333")
PROVENANCE_ID = uuid.UUID("44444444-4444-4444-8444-444444444444")


def _revision(
    *,
    valid_from_us: int | None = None,
    valid_to_us: int | None = None,
) -> KnowledgeUnitRevision:
    return KnowledgeUnitRevision(
        knowledge_id=KNOWLEDGE_ID,
        revision_id=REVISION_ID,
        revision_no=3,
        created_at_us=100,
        created_by_actor_id=ACTOR_ID,
        provenance_id=PROVENANCE_ID,
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            title="Temporal fact",
            body="Recorded canonical knowledge.",
            valid_from_us=valid_from_us,
            valid_to_us=valid_to_us,
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )


def test_expired_validity_emits_stale_signal_without_truth_reclassification() -> None:
    revision = _revision(valid_from_us=10, valid_to_us=20)
    assessment = KnowledgeStalenessPolicy.assess(revision, assessed_at_us=21)
    assert assessment.state is KnowledgeStalenessState.STALE_BY_VALIDITY
    assert assessment.reasons == (KnowledgeStalenessReason.VALIDITY_ENDED,)
    assert assessment.should_signal_stale is True
    assert assessment.knowledge_id == str(KNOWLEDGE_ID)
    assert assessment.revision_id == str(REVISION_ID)
    assert revision.payload.epistemic_status is EpistemicStatus.SUPPORTED


def test_source_age_emits_stale_signal_only_from_explicit_age_evidence() -> None:
    assessment = KnowledgeStalenessPolicy.assess(
        _revision(),
        assessed_at_us=1_000,
        source_observed_at_us=100,
        max_source_age_us=500,
    )
    assert assessment.state is KnowledgeStalenessState.STALE_BY_SOURCE_AGE
    assert assessment.reasons == (KnowledgeStalenessReason.SOURCE_AGE_EXCEEDED,)
    assert assessment.should_signal_stale is True
    assert assessment.source_observed_at_us == 100
    assert assessment.max_source_age_us == 500


def test_multiple_stale_signals_are_preserved_deterministically() -> None:
    assessment = KnowledgeStalenessPolicy.assess(
        _revision(valid_to_us=900),
        assessed_at_us=1_000,
        source_observed_at_us=100,
        max_source_age_us=500,
    )
    assert assessment.state is KnowledgeStalenessState.STALE_BY_MULTIPLE_SIGNALS
    assert assessment.reasons == (
        KnowledgeStalenessReason.VALIDITY_ENDED,
        KnowledgeStalenessReason.SOURCE_AGE_EXCEEDED,
    )


def test_age_boundary_is_not_stale() -> None:
    assessment = KnowledgeStalenessPolicy.assess(
        _revision(),
        assessed_at_us=1_000,
        source_observed_at_us=500,
        max_source_age_us=500,
    )
    assert assessment.state is KnowledgeStalenessState.NOT_STALE_BY_RECORDED_EVIDENCE
    assert assessment.reasons == ()
    assert assessment.should_signal_stale is False


def test_validity_boundary_is_not_stale_before_it_has_expired() -> None:
    assessment = KnowledgeStalenessPolicy.assess(
        _revision(valid_from_us=10, valid_to_us=20),
        assessed_at_us=20,
    )
    assert assessment.state is KnowledgeStalenessState.NOT_STALE_BY_RECORDED_EVIDENCE
    assert assessment.should_signal_stale is False


def test_open_ended_validity_without_source_age_does_not_invent_freshness() -> None:
    assessment = KnowledgeStalenessPolicy.assess(
        _revision(valid_from_us=10),
        assessed_at_us=1_000,
    )
    assert assessment.state is KnowledgeStalenessState.INSUFFICIENT_TEMPORAL_EVIDENCE
    assert assessment.should_signal_stale is False
    assert assessment.valid_to_us is None


def test_future_validity_is_not_misclassified_as_stale() -> None:
    assessment = KnowledgeStalenessPolicy.assess(
        _revision(valid_from_us=200, valid_to_us=300),
        assessed_at_us=100,
    )
    assert assessment.state is KnowledgeStalenessState.NOT_STALE_BY_RECORDED_EVIDENCE
    assert assessment.should_signal_stale is False


@pytest.mark.parametrize("assessed_at_us", [True, 1.5, "100"])
def test_assessment_rejects_non_integer_time(assessed_at_us: object) -> None:
    with pytest.raises(TypeError, match="assessed_at_us must be an integer"):
        KnowledgeStalenessPolicy.assess(
            _revision(valid_to_us=20),
            assessed_at_us=cast(int, assessed_at_us),
        )


def test_assessment_rejects_negative_time() -> None:
    with pytest.raises(ValueError, match="assessed_at_us must not be negative"):
        KnowledgeStalenessPolicy.assess(_revision(valid_to_us=20), assessed_at_us=-1)


@pytest.mark.parametrize(
    ("source_observed_at_us", "max_source_age_us"),
    [(100, None), (None, 500)],
)
def test_source_age_evidence_must_be_supplied_as_a_pair(
    source_observed_at_us: int | None,
    max_source_age_us: int | None,
) -> None:
    with pytest.raises(ValueError, match="must be supplied together"):
        KnowledgeStalenessPolicy.assess(
            _revision(),
            assessed_at_us=1_000,
            source_observed_at_us=source_observed_at_us,
            max_source_age_us=max_source_age_us,
        )


@pytest.mark.parametrize(
    ("source_observed_at_us", "max_source_age_us", "message"),
    [
        (True, 500, "source_observed_at_us must be an integer"),
        (-1, 500, "source_observed_at_us must not be negative"),
        (100, True, "max_source_age_us must be an integer"),
        (100, -1, "max_source_age_us must not be negative"),
    ],
)
def test_source_age_evidence_rejects_invalid_values(
    source_observed_at_us: object,
    max_source_age_us: object,
    message: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        KnowledgeStalenessPolicy.assess(
            _revision(),
            assessed_at_us=1_000,
            source_observed_at_us=cast(int, source_observed_at_us),
            max_source_age_us=cast(int, max_source_age_us),
        )


def test_future_source_observation_fails_closed() -> None:
    with pytest.raises(ValueError, match="must not be in the future"):
        KnowledgeStalenessPolicy.assess(
            _revision(),
            assessed_at_us=100,
            source_observed_at_us=101,
            max_source_age_us=50,
        )


def test_assessment_rejects_non_revision_input() -> None:
    with pytest.raises(TypeError, match="KnowledgeUnitRevision"):
        KnowledgeStalenessPolicy.assess(
            cast(KnowledgeUnitRevision, object()),
            assessed_at_us=100,
        )
