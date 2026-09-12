from __future__ import annotations

import uuid

import pytest

from athena.api.knowledge_explanation import KnowledgeExplanationApiService
from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
    ProvenanceInputRef,
)

KNOWLEDGE_ID = uuid.UUID("00000000-0000-7000-8000-000000000001")
REVISION_ID = uuid.UUID("00000000-0000-7000-8000-000000000002")
ACTOR_ID = uuid.UUID("00000000-0000-7000-8000-000000000003")
PROVENANCE_ID = uuid.UUID("00000000-0000-7000-8000-000000000004")
SOURCE_ID = uuid.UUID("00000000-0000-7000-8000-000000000005")
SOURCE_REVISION_ID = uuid.UUID("00000000-0000-7000-8000-000000000006")


def _snapshot() -> KnowledgeUnitSnapshot:
    revision = KnowledgeUnitRevision(
        knowledge_id=KNOWLEDGE_ID,
        revision_id=REVISION_ID,
        revision_no=2,
        created_at_us=1_800_000,
        created_by_actor_id=ACTOR_ID,
        provenance_id=PROVENANCE_ID,
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            title="Recorded fact",
            body="Canonical body",
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )
    return KnowledgeUnitSnapshot(
        knowledge_id=KNOWLEDGE_ID,
        lifecycle_state="active",
        revision=revision,
    )


class _Reader:
    def __init__(self, inputs: tuple[ProvenanceInputRef, ...]) -> None:
        self.inputs = inputs
        self.loaded: list[uuid.UUID] = []
        self.requested_provenance: list[uuid.UUID] = []

    def load(self, knowledge_id: uuid.UUID) -> KnowledgeUnitSnapshot:
        self.loaded.append(knowledge_id)
        return _snapshot()

    def provenance_inputs(
        self,
        provenance_id: uuid.UUID,
    ) -> tuple[ProvenanceInputRef, ...]:
        self.requested_provenance.append(provenance_id)
        return self.inputs


def test_why_known_uses_current_revision_and_recorded_inputs() -> None:
    reader = _Reader(
        (
            ProvenanceInputRef(
                provenance_id=PROVENANCE_ID,
                input_entity_id=SOURCE_ID,
                input_revision_id=SOURCE_REVISION_ID,
                input_role="chat_message_source",
                ordinal=0,
            ),
        )
    )
    api = KnowledgeExplanationApiService(knowledge=reader)

    response = api.why_known(str(KNOWLEDGE_ID))

    assert reader.loaded == [KNOWLEDGE_ID]
    assert reader.requested_provenance == [PROVENANCE_ID]
    assert response.knowledge_id == str(KNOWLEDGE_ID)
    assert response.revision_id == str(REVISION_ID)
    assert response.revision_no == 2
    assert response.actor_id == str(ACTOR_ID)
    assert response.inputs[0].entity_id == str(SOURCE_ID)
    assert response.inputs[0].revision_id == str(SOURCE_REVISION_ID)
    assert response.inputs[0].role == "chat_message_source"
    assert response.inputs[0].ordinal == 0
    assert "Recorded provenance inputs" in response.text


def test_why_known_preserves_explicit_source_free_explanation() -> None:
    api = KnowledgeExplanationApiService(knowledge=_Reader(()))

    response = api.why_known(str(KNOWLEDGE_ID))

    assert response.inputs == ()
    assert "No provenance inputs are recorded" in response.text


def test_why_known_rejects_invalid_identifier_before_repository_access() -> None:
    reader = _Reader(())
    api = KnowledgeExplanationApiService(knowledge=reader)

    with pytest.raises(ValueError):
        api.why_known("not-a-uuid")

    assert reader.loaded == []
    assert reader.requested_provenance == []
