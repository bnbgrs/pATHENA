"""Transport-neutral export projection for canonical Personal Memory."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemoryScopeKind,
    MemorySensitivity,
    PersonalMemorySnapshot,
)


class PersonalMemoryExportProtectionError(ValueError):
    """Raised when plaintext export would expose Protected Personal Memory."""


@dataclass(frozen=True, slots=True)
class PersonalMemoryExportEntry:
    """One canonical current Memory entry prepared for a separate export surface."""

    memory_id: uuid.UUID
    revision_id: uuid.UUID
    revision_no: int
    lifecycle_state: str
    content: str
    memory_kind: MemoryKind
    scope_kind: MemoryScopeKind
    scope_entity_id: uuid.UUID | None
    origin: MemoryLearningMode
    sensitivity: MemorySensitivity
    confidence: float | None
    last_confirmed_at_us: int | None


def export_personal_memory(
    snapshots: tuple[PersonalMemorySnapshot, ...],
) -> tuple[PersonalMemoryExportEntry, ...]:
    """Project canonical Memory independently without weakening Protected Content.

    The ordinary plaintext export path rejects Protected entries. A caller that
    needs Protected export must use the dedicated Protected Content mechanism so
    ciphertext/protection metadata are preserved instead of materializing
    plaintext here.
    """
    entries: list[PersonalMemoryExportEntry] = []
    seen_memory_ids: set[uuid.UUID] = set()
    for snapshot in snapshots:
        if snapshot.memory_id in seen_memory_ids:
            raise ValueError("Personal Memory export requires one current snapshot per memory_id.")
        seen_memory_ids.add(snapshot.memory_id)

        revision = snapshot.revision
        if revision.memory_id != snapshot.memory_id:
            raise ValueError("Personal Memory export snapshot/revision identity mismatch.")
        payload = revision.payload
        if payload.sensitivity is MemorySensitivity.PROTECTED:
            raise PersonalMemoryExportProtectionError(
                "Protected Personal Memory requires the Protected Content export path."
            )

        entries.append(
            PersonalMemoryExportEntry(
                memory_id=snapshot.memory_id,
                revision_id=revision.revision_id,
                revision_no=revision.revision_no,
                lifecycle_state=snapshot.lifecycle_state,
                content=payload.content,
                memory_kind=payload.memory_kind,
                scope_kind=payload.scope_kind,
                scope_entity_id=payload.scope_entity_id,
                origin=payload.learning_mode,
                sensitivity=payload.sensitivity,
                confidence=payload.confidence,
                last_confirmed_at_us=payload.last_confirmed_at_us,
            )
        )
    return tuple(entries)
