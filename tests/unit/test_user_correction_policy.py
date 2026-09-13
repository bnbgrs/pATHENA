from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
)
from athena.knowledge.user_correction_policy import (
    UserCorrectionPolicy,
    UserCorrectionState,
)


USER_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
MODEL_ID = uuid.UUID("20000000-0000-0000-0000-000000000002")
SYSTEM_ID = uuid.UUID("30000000-0000-0000-0000-000000000003")


def _revision(*, actor_id: uuid.UUID, created_at_us: int = 100) -> KnowledgeUnitRevision:
    return KnowledgeUnitRevision(
        knowledge_id=uuid.UUID("40000000-0000-0000-0000-000000000004"),
        revision_id=uuid.UUID("50000000-0000-0000-0000-000000000005"),
        revision_no=2,
        created_at_us=created_at_us,
        created_by_actor_id=actor_id,
        provenance_id=uuid.UUID("60000000-0000-0000-0000-000000000006"),
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            body="User-confirmed canonical text.",
            epistemic_status=EpistemicStatus.ASSERTED,
        ),
    )


def test_non_user_revision_does_not_gain_special_user_lock() -> None:
    assessment = UserCorrectionPolicy.assess(
        _revision(actor_id=SYSTEM_ID),
        user_actor_id=USER_ID,
        incoming_actor_id=MODEL_ID,
    )

    assert assessment.state is UserCorrectionState.NOT_USER_CORRECTION
    assert assessment.permits_automatic_replacement is True
    assert assessment.requires_human_review is False


def test_user_correction_is_preserved_without_newer_evidence() -> None:
    assessment = UserCorrectionPolicy.assess(
        _revision(actor_id=USER_ID),
        user_actor_id=USER_ID,
        incoming_actor_id=MODEL_ID,
    )

    assert assessment.state is UserCorrectionState.PRESERVE_USER_CORRECTION
    assert assessment.permits_automatic_replacement is False
    assert assessment.requires_human_review is False


@pytest.mark.parametrize("evidence_time", [50, 100])
def test_old_or_equal_evidence_does_not_override_user_correction(evidence_time: int) -> None:
    assessment = UserCorrectionPolicy.assess(
        _revision(actor_id=USER_ID, created_at_us=100),
        user_actor_id=USER_ID,
        incoming_actor_id=MODEL_ID,
        newest_evidence_at_us=evidence_time,
    )

    assert assessment.state is UserCorrectionState.PRESERVE_USER_CORRECTION
    assert assessment.permits_automatic_replacement is False


def test_newer_evidence_requires_review_instead_of_silent_replacement() -> None:
    assessment = UserCorrectionPolicy.assess(
        _revision(actor_id=USER_ID, created_at_us=100),
        user_actor_id=USER_ID,
        incoming_actor_id=MODEL_ID,
        newest_evidence_at_us=101,
    )

    assert assessment.state is UserCorrectionState.NEW_EVIDENCE_REVIEW_REQUIRED
    assert assessment.requires_human_review is True
    assert assessment.permits_automatic_replacement is False
    assert assessment.newest_evidence_at_us == 101


def test_later_explicit_user_decision_can_revise_previous_user_correction() -> None:
    assessment = UserCorrectionPolicy.assess(
        _revision(actor_id=USER_ID),
        user_actor_id=USER_ID,
        incoming_actor_id=USER_ID,
    )

    assert assessment.state is UserCorrectionState.EXPLICIT_USER_REVISION
    assert assessment.permits_explicit_user_revision is True
    assert assessment.permits_automatic_replacement is False


@pytest.mark.parametrize("value", [True, -1, 1.5, "101"])
def test_invalid_evidence_timestamp_fails_closed(value: object) -> None:
    expected = ValueError if value == -1 else TypeError
    with pytest.raises(expected):
        UserCorrectionPolicy.assess(
            _revision(actor_id=USER_ID),
            user_actor_id=USER_ID,
            incoming_actor_id=MODEL_ID,
            newest_evidence_at_us=value,  # type: ignore[arg-type]
        )


def test_actor_ids_must_be_real_uuids() -> None:
    with pytest.raises(TypeError, match="user_actor_id"):
        UserCorrectionPolicy.assess(
            _revision(actor_id=USER_ID),
            user_actor_id="user",  # type: ignore[arg-type]
            incoming_actor_id=MODEL_ID,
        )
    with pytest.raises(TypeError, match="incoming_actor_id"):
        UserCorrectionPolicy.assess(
            _revision(actor_id=USER_ID),
            user_actor_id=USER_ID,
            incoming_actor_id="model",  # type: ignore[arg-type]
        )
