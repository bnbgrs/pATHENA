"""Transport-neutral projections for the Personal Memory management view."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemoryScopeKind,
    MemorySensitivity,
    PersonalMemoryRevision,
    PersonalMemorySnapshot,
)


class PersonalMemoryViewProtectionError(ValueError):
    """Raised when plaintext view composition would expose Protected Memory."""


@dataclass(frozen=True, slots=True)
class PersonalMemoryRevisionSummary:
    """Content-free historical revision metadata for the Memory view."""

    revision_id: uuid.UUID
    revision_no: int
    created_at_us: int
    origin: MemoryLearningMode
    last_confirmed_at_us: int | None


@dataclass(frozen=True, slots=True)
class PersonalMemoryView:
    """Canonical read-only Personal Memory view derived from durable state."""

    memory_id: uuid.UUID
    current_revision_id: uuid.UUID
    lifecycle_state: str
    content: str
    memory_kind: MemoryKind
    scope_kind: MemoryScopeKind
    scope_entity_id: uuid.UUID | None
    origin: MemoryLearningMode
    sensitivity: MemorySensitivity
    confidence: float | None
    last_confirmed_at_us: int | None
    revisions: tuple[PersonalMemoryRevisionSummary, ...]


def personal_memory_view(
    snapshot: PersonalMemorySnapshot,
    revisions: tuple[PersonalMemoryRevision, ...],
) -> PersonalMemoryView:
    """Project one canonical Memory entry without synthesizing metadata.

    Protected Memory requires the Protected Content path and is therefore
    rejected rather than exposing plaintext content or metadata through this
    ordinary view projection.
    """
    current = snapshot.revision
    payload = current.payload
    if payload.sensitivity is MemorySensitivity.PROTECTED:
        raise PersonalMemoryViewProtectionError(
            "Protected Personal Memory requires the Protected Content view path."
        )
    if not revisions:
        raise ValueError("Personal Memory view requires canonical revision history.")
    if any(revision.memory_id != snapshot.memory_id for revision in revisions):
        raise ValueError("Personal Memory view revisions must belong to the same memory_id.")
    if tuple(revision.revision_no for revision in revisions) != tuple(
        range(1, len(revisions) + 1)
    ):
        raise ValueError("Personal Memory view requires contiguous canonical revision history.")
    if revisions[-1].revision_id != current.revision_id:
        raise ValueError("Personal Memory view history must end at the current revision.")

    return PersonalMemoryView(
        memory_id=snapshot.memory_id,
        current_revision_id=current.revision_id,
        lifecycle_state=snapshot.lifecycle_state,
        content=payload.content,
        memory_kind=payload.memory_kind,
        scope_kind=payload.scope_kind,
        scope_entity_id=payload.scope_entity_id,
        origin=payload.learning_mode,
        sensitivity=payload.sensitivity,
        confidence=payload.confidence,
        last_confirmed_at_us=payload.last_confirmed_at_us,
        revisions=tuple(
            PersonalMemoryRevisionSummary(
                revision_id=revision.revision_id,
                revision_no=revision.revision_no,
                created_at_us=revision.created_at_us,
                origin=revision.payload.learning_mode,
                last_confirmed_at_us=revision.payload.last_confirmed_at_us,
            )
            for revision in revisions
        ),
    )
