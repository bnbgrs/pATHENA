from __future__ import annotations

import uuid

import pytest

from athena.memory.models import (
    MemoryKind,
    MemorySensitivity,
    PersonalMemoryDraft,
    PersonalMemoryRevision,
    PersonalMemorySnapshot,
)
from athena.memory.review import stale_personal_memory_reviews


def _snapshot(
    *,
    memory_id: uuid.UUID,
    revision_id: uuid.UUID,
    last_confirmed_at_us: int | None,
    lifecycle_state: str = "active",
    sensitivity: MemorySensitivity = MemorySensitivity.NORMAL,
) -> PersonalMemorySnapshot:
    actor_id = uuid.uuid4()
    return PersonalMemorySnapshot(
        memory_id=memory_id,
        lifecycle_state=lifecycle_state,
        revision=PersonalMemoryRevision(
            memory_id=memory_id,
            revision_id=revision_id,
            revision_no=1,
            created_at_us=10,
            created_by_actor_id=actor_id,
            provenance_id=uuid.uuid4(),
            payload=PersonalMemoryDraft(
                memory_kind=MemoryKind.RESPONSE_STYLE,
                content="Use concise answers.",
                sensitivity=sensitivity,
                last_confirmed_at_us=last_confirmed_at_us,
            ),
        ),
    )


def test_stale_review_projects_only_real_content_free_identity_and_age() -> None:
    memory_id = uuid.uuid4()
    revision_id = uuid.uuid4()
    snapshot = _snapshot(
        memory_id=memory_id,
        revision_id=revision_id,
        last_confirmed_at_us=100,
        sensitivity=MemorySensitivity.PROTECTED,
    )

    markers = stale_personal_memory_reviews((snapshot,), now_us=500, stale_after_us=300)

    assert len(markers) == 1
    marker = markers[0]
    assert marker.memory_id == memory_id
    assert marker.revision_id == revision_id
    assert marker.last_confirmed_at_us == 100
    assert marker.age_us == 400
    assert not hasattr(marker, "content")


def test_stale_review_omits_fresh_inactive_and_unconfirmed_memory() -> None:
    snapshots = (
        _snapshot(
            memory_id=uuid.uuid4(),
            revision_id=uuid.uuid4(),
            last_confirmed_at_us=450,
        ),
        _snapshot(
            memory_id=uuid.uuid4(),
            revision_id=uuid.uuid4(),
            last_confirmed_at_us=100,
            lifecycle_state="inactive",
        ),
        _snapshot(
            memory_id=uuid.uuid4(),
            revision_id=uuid.uuid4(),
            last_confirmed_at_us=None,
        ),
    )

    assert stale_personal_memory_reviews(snapshots, now_us=500, stale_after_us=300) == ()


def test_stale_review_fails_closed_for_duplicate_current_identity() -> None:
    memory_id = uuid.uuid4()
    snapshots = (
        _snapshot(
            memory_id=memory_id,
            revision_id=uuid.uuid4(),
            last_confirmed_at_us=100,
        ),
        _snapshot(
            memory_id=memory_id,
            revision_id=uuid.uuid4(),
            last_confirmed_at_us=100,
        ),
    )

    with pytest.raises(ValueError, match="duplicate current identities"):
        stale_personal_memory_reviews(snapshots, now_us=500, stale_after_us=300)


def test_stale_review_fails_closed_for_snapshot_revision_identity_mismatch() -> None:
    snapshot = _snapshot(
        memory_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        last_confirmed_at_us=100,
    )
    mismatched = PersonalMemorySnapshot(
        memory_id=uuid.uuid4(),
        lifecycle_state=snapshot.lifecycle_state,
        revision=snapshot.revision,
    )

    with pytest.raises(ValueError, match="snapshot/revision identity mismatch"):
        stale_personal_memory_reviews((mismatched,), now_us=500, stale_after_us=300)


def test_stale_review_rejects_future_confirmation_and_invalid_clock_inputs() -> None:
    snapshot = _snapshot(
        memory_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        last_confirmed_at_us=501,
    )

    with pytest.raises(ValueError, match="must not be in the future"):
        stale_personal_memory_reviews((snapshot,), now_us=500, stale_after_us=300)
    with pytest.raises(ValueError, match="now_us"):
        stale_personal_memory_reviews((), now_us=-1, stale_after_us=300)
    with pytest.raises(ValueError, match="stale_after_us"):
        stale_personal_memory_reviews((), now_us=500, stale_after_us=0)
