"""Read-only review eligibility for canonical ATHENA Personal Memory."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import PersonalMemorySnapshot


@dataclass(frozen=True, slots=True)
class PersonalMemoryReviewMarker:
    """Content-free marker that one active preference is stale enough for review."""

    memory_id: uuid.UUID
    revision_id: uuid.UUID
    last_confirmed_at_us: int
    age_us: int


def stale_personal_memory_reviews(
    snapshots: tuple[PersonalMemorySnapshot, ...],
    *,
    now_us: int,
    stale_after_us: int,
) -> tuple[PersonalMemoryReviewMarker, ...]:
    """Return deterministic review markers without mutating or deleting Memory.

    Only active canonical snapshots with a real ``last_confirmed_at_us`` participate.
    Unconfirmed entries are not assigned a synthetic confirmation time. Protected
    payload content is never copied into the projection.
    """
    if type(now_us) is not int or now_us < 0:
        raise ValueError("now_us must be a non-negative integer.")
    if type(stale_after_us) is not int or stale_after_us <= 0:
        raise ValueError("stale_after_us must be a positive integer.")

    seen_memory_ids: set[uuid.UUID] = set()
    markers: list[PersonalMemoryReviewMarker] = []

    for snapshot in snapshots:
        memory_id = snapshot.memory_id
        revision = snapshot.revision
        if memory_id in seen_memory_ids:
            raise ValueError("Personal Memory review input contains duplicate current identities.")
        seen_memory_ids.add(memory_id)

        if revision.memory_id != memory_id:
            raise ValueError("Personal Memory snapshot/revision identity mismatch.")
        if snapshot.lifecycle_state != "active":
            continue

        last_confirmed_at_us = revision.payload.last_confirmed_at_us
        if last_confirmed_at_us is None:
            continue
        if last_confirmed_at_us > now_us:
            raise ValueError("Personal Memory confirmation time must not be in the future.")

        age_us = now_us - last_confirmed_at_us
        if age_us < stale_after_us:
            continue
        markers.append(
            PersonalMemoryReviewMarker(
                memory_id=memory_id,
                revision_id=revision.revision_id,
                last_confirmed_at_us=last_confirmed_at_us,
                age_us=age_us,
            )
        )

    return tuple(markers)
