"""Transport-neutral Personal Memory context projection."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import (
    MemoryScopeKind,
    MemorySensitivity,
    PersonalMemorySnapshot,
)


PERSONAL_MEMORY_CONTEXT_LABEL = "USER PREFERENCE"


class PersonalMemoryContextProtectionError(ValueError):
    """Raised when ordinary context composition would expose Protected Memory."""


@dataclass(frozen=True, slots=True)
class PersonalMemoryContextEntry:
    """One canonical active Personal Memory entry for model context composition."""

    label: str
    memory_id: uuid.UUID
    revision_id: uuid.UUID
    content: str
    scope_kind: MemoryScopeKind
    scope_entity_id: uuid.UUID | None


def personal_memory_context(
    snapshots: tuple[PersonalMemorySnapshot, ...],
) -> tuple[PersonalMemoryContextEntry, ...]:
    """Project active canonical Memory as explicitly labeled user preferences.

    Protected Memory is rejected from the ordinary plaintext context path. The
    dedicated Protected Content mechanism must materialize it after authorization.
    Inactive Memory is omitted rather than allowed to influence the current turn.
    """
    entries: list[PersonalMemoryContextEntry] = []
    seen_memory_ids: set[uuid.UUID] = set()
    for snapshot in snapshots:
        if snapshot.memory_id in seen_memory_ids:
            raise ValueError("Personal Memory context requires one current snapshot per memory_id.")
        seen_memory_ids.add(snapshot.memory_id)

        revision = snapshot.revision
        if revision.memory_id != snapshot.memory_id:
            raise ValueError("Personal Memory context snapshot/revision identity mismatch.")
        if snapshot.lifecycle_state != "active":
            continue
        payload = revision.payload
        if payload.sensitivity is MemorySensitivity.PROTECTED:
            raise PersonalMemoryContextProtectionError(
                "Protected Personal Memory requires the Protected Content context path."
            )

        entries.append(
            PersonalMemoryContextEntry(
                label=PERSONAL_MEMORY_CONTEXT_LABEL,
                memory_id=snapshot.memory_id,
                revision_id=revision.revision_id,
                content=payload.content,
                scope_kind=payload.scope_kind,
                scope_entity_id=payload.scope_entity_id,
            )
        )
    return tuple(entries)
