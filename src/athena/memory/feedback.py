"""Content-free feedback projection for rejected Personal-Memory proposals."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import (
    MemoryKind,
    MemoryScopeKind,
    ModelInferredMemoryProposal,
)


@dataclass(frozen=True, slots=True)
class RejectedPersonalMemoryFeedback:
    """Technical rejection marker that deliberately excludes proposed content."""

    model_signature_id: uuid.UUID
    processing_run_id: uuid.UUID
    memory_kind: MemoryKind
    scope_kind: MemoryScopeKind
    scope_entity_id: uuid.UUID | None


def rejected_personal_memory_feedback(
    proposal: ModelInferredMemoryProposal,
) -> RejectedPersonalMemoryFeedback:
    """Project rejection feedback without retaining the rejected preference text.

    The projection preserves only real proposal provenance and non-content routing
    metadata. It creates no durable row, no synthetic identifier, and no canonical
    Personal-Memory revision; persistence remains an explicit caller-owned choice.
    """
    if type(proposal) is not ModelInferredMemoryProposal:
        raise TypeError("Rejected Personal Memory feedback requires ModelInferredMemoryProposal.")

    draft = proposal.draft
    return RejectedPersonalMemoryFeedback(
        model_signature_id=proposal.model_signature_id,
        processing_run_id=proposal.processing_run_id,
        memory_kind=draft.memory_kind,
        scope_kind=draft.scope_kind,
        scope_entity_id=draft.scope_entity_id,
    )
