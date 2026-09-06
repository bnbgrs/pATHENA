"""Truthful read-only explanations for canonical Personal Memory entries."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import MemoryLearningMode, PersonalMemorySnapshot


@dataclass(frozen=True, slots=True)
class PersonalMemoryExplanation:
    """Transport-neutral explanation derived only from canonical Memory state."""

    memory_id: uuid.UUID
    revision_id: uuid.UUID
    origin: MemoryLearningMode
    last_changed_at_us: int
    last_confirmed_at_us: int | None


def explain_personal_memory(snapshot: PersonalMemorySnapshot) -> PersonalMemoryExplanation:
    """Explain why one current Memory exists without inventing provenance facts or exposing content."""
    revision = snapshot.revision
    return PersonalMemoryExplanation(
        memory_id=snapshot.memory_id,
        revision_id=revision.revision_id,
        origin=revision.payload.learning_mode,
        last_changed_at_us=revision.created_at_us,
        last_confirmed_at_us=revision.payload.last_confirmed_at_us,
    )
