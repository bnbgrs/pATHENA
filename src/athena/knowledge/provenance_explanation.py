"""Truthful human-readable provenance explanations for canonical Knowledge revisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import uuid

from athena.knowledge.models import KnowledgeUnitRevision, ProvenanceInputRef


@dataclass(frozen=True, slots=True)
class ProvenanceExplanationInput:
    """One provenance input exposed without inventing source metadata."""

    entity_id: uuid.UUID
    revision_id: uuid.UUID | None
    role: str
    ordinal: int


@dataclass(frozen=True, slots=True)
class KnowledgeProvenanceExplanation:
    """Transport-neutral answer to "why do you know this?" for one revision."""

    knowledge_id: uuid.UUID
    revision_id: uuid.UUID
    revision_no: int
    created_at_us: int
    actor_id: uuid.UUID
    inputs: tuple[ProvenanceExplanationInput, ...]
    text: str


def explain_knowledge_provenance(
    revision: KnowledgeUnitRevision,
    provenance_inputs: tuple[ProvenanceInputRef, ...],
) -> KnowledgeProvenanceExplanation:
    """Project recorded provenance into a readable explanation without fabrication."""
    if not isinstance(revision, KnowledgeUnitRevision):
        raise TypeError("revision must be a KnowledgeUnitRevision.")
    if not isinstance(provenance_inputs, tuple):
        raise TypeError("provenance_inputs must be a tuple.")

    seen_ordinals: set[int] = set()
    projected: list[ProvenanceExplanationInput] = []
    for item in provenance_inputs:
        if not isinstance(item, ProvenanceInputRef):
            raise TypeError("provenance_inputs must contain ProvenanceInputRef values.")
        if item.provenance_id != revision.provenance_id:
            raise ValueError("Provenance input belongs to a different provenance record.")
        if item.ordinal in seen_ordinals:
            raise ValueError("Provenance input ordinals must be unique.")
        seen_ordinals.add(item.ordinal)
        projected.append(
            ProvenanceExplanationInput(
                entity_id=item.input_entity_id,
                revision_id=item.input_revision_id,
                role=item.input_role,
                ordinal=item.ordinal,
            )
        )

    inputs = tuple(sorted(projected, key=lambda item: item.ordinal))
    created_at = datetime.fromtimestamp(revision.created_at_us / 1_000_000, tz=UTC).isoformat()
    prefix = (
        f"Knowledge revision {revision.revision_no} was recorded at {created_at} "
        f"by actor {revision.created_by_actor_id}."
    )
    if not inputs:
        text = f"{prefix} No provenance inputs are recorded for this revision."
    else:
        rendered = "; ".join(_render_input(item) for item in inputs)
        text = f"{prefix} Recorded provenance inputs: {rendered}."

    return KnowledgeProvenanceExplanation(
        knowledge_id=revision.knowledge_id,
        revision_id=revision.revision_id,
        revision_no=revision.revision_no,
        created_at_us=revision.created_at_us,
        actor_id=revision.created_by_actor_id,
        inputs=inputs,
        text=text,
    )


def _render_input(item: ProvenanceExplanationInput) -> str:
    if item.revision_id is None:
        return f"{item.role} entity {item.entity_id}"
    return f"{item.role} entity {item.entity_id} revision {item.revision_id}"
