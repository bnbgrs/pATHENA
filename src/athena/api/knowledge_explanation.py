"""Transport-neutral API composition for truthful Knowledge provenance explanations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

from athena.knowledge.models import KnowledgeUnitSnapshot, ProvenanceInputRef
from athena.knowledge.provenance_explanation import explain_knowledge_provenance


class KnowledgeProvenanceReader(Protocol):
    """Minimal read boundary required by the provenance explanation API."""

    def load(self, knowledge_id: uuid.UUID) -> KnowledgeUnitSnapshot: ...

    def provenance_inputs(
        self,
        provenance_id: uuid.UUID,
    ) -> tuple[ProvenanceInputRef, ...]: ...


@dataclass(frozen=True, slots=True)
class KnowledgeProvenanceInputResponse:
    entity_id: str
    revision_id: str | None
    role: str
    ordinal: int


@dataclass(frozen=True, slots=True)
class KnowledgeProvenanceExplanationResponse:
    knowledge_id: str
    revision_id: str
    revision_no: int
    created_at_us: int
    actor_id: str
    inputs: tuple[KnowledgeProvenanceInputResponse, ...]
    text: str


class KnowledgeExplanationApiService:
    """Expose recorded Knowledge provenance without inventing source metadata."""

    def __init__(self, *, knowledge: KnowledgeProvenanceReader) -> None:
        self._knowledge = knowledge

    def why_known(self, knowledge_id: str) -> KnowledgeProvenanceExplanationResponse:
        """Explain why the current Knowledge revision is known from recorded facts."""
        parsed_id = uuid.UUID(knowledge_id)
        snapshot = self._knowledge.load(parsed_id)
        revision = snapshot.revision
        explanation = explain_knowledge_provenance(
            revision,
            self._knowledge.provenance_inputs(revision.provenance_id),
        )
        return KnowledgeProvenanceExplanationResponse(
            knowledge_id=str(explanation.knowledge_id),
            revision_id=str(explanation.revision_id),
            revision_no=explanation.revision_no,
            created_at_us=explanation.created_at_us,
            actor_id=str(explanation.actor_id),
            inputs=tuple(
                KnowledgeProvenanceInputResponse(
                    entity_id=str(item.entity_id),
                    revision_id=(
                        None if item.revision_id is None else str(item.revision_id)
                    ),
                    role=item.role,
                    ordinal=item.ordinal,
                )
                for item in explanation.inputs
            ),
            text=explanation.text,
        )
