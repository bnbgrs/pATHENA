import uuid

import pytest

from athena.knowledge.models import (
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    ProvenanceInputRef,
)
from athena.knowledge.provenance_explanation import explain_knowledge_provenance


def _revision() -> KnowledgeUnitRevision:
    return KnowledgeUnitRevision(
        knowledge_id=uuid.UUID("00000000-0000-7000-8000-000000000001"),
        revision_id=uuid.UUID("00000000-0000-7000-8000-000000000002"),
        revision_no=2,
        created_at_us=1_000_000,
        created_by_actor_id=uuid.UUID("00000000-0000-7000-8000-000000000003"),
        provenance_id=uuid.UUID("00000000-0000-7000-8000-000000000004"),
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            body="Recorded fact",
        ),
    )


def test_explains_recorded_inputs_in_provenance_order() -> None:
    revision = _revision()
    first_entity = uuid.UUID("00000000-0000-7000-8000-000000000010")
    first_revision = uuid.UUID("00000000-0000-7000-8000-000000000011")
    second_entity = uuid.UUID("00000000-0000-7000-8000-000000000020")
    inputs = (
        ProvenanceInputRef(
            provenance_id=revision.provenance_id,
            input_entity_id=second_entity,
            input_revision_id=None,
            input_role="context",
            ordinal=1,
        ),
        ProvenanceInputRef(
            provenance_id=revision.provenance_id,
            input_entity_id=first_entity,
            input_revision_id=first_revision,
            input_role="source",
            ordinal=0,
        ),
    )

    explanation = explain_knowledge_provenance(revision, inputs)

    assert explanation.knowledge_id == revision.knowledge_id
    assert explanation.revision_id == revision.revision_id
    assert explanation.actor_id == revision.created_by_actor_id
    assert tuple(item.ordinal for item in explanation.inputs) == (0, 1)
    assert str(first_entity) in explanation.text
    assert str(first_revision) in explanation.text
    assert str(second_entity) in explanation.text
    assert explanation.text.index(str(first_entity)) < explanation.text.index(str(second_entity))
    assert "1970-01-01T00:00:01+00:00" in explanation.text


def test_empty_provenance_is_explicit_instead_of_fabricating_a_source() -> None:
    revision = _revision()

    explanation = explain_knowledge_provenance(revision, ())

    assert explanation.inputs == ()
    assert "No provenance inputs are recorded for this revision." in explanation.text


def test_rejects_input_from_another_provenance_record() -> None:
    revision = _revision()
    foreign = ProvenanceInputRef(
        provenance_id=uuid.UUID("00000000-0000-7000-8000-000000000099"),
        input_entity_id=uuid.UUID("00000000-0000-7000-8000-000000000010"),
        input_revision_id=None,
        input_role="source",
        ordinal=0,
    )

    with pytest.raises(ValueError, match="different provenance record"):
        explain_knowledge_provenance(revision, (foreign,))


def test_rejects_duplicate_ordinals() -> None:
    revision = _revision()
    inputs = tuple(
        ProvenanceInputRef(
            provenance_id=revision.provenance_id,
            input_entity_id=uuid.uuid4(),
            input_revision_id=None,
            input_role="source",
            ordinal=0,
        )
        for _ in range(2)
    )

    with pytest.raises(ValueError, match="ordinals must be unique"):
        explain_knowledge_provenance(revision, inputs)


@pytest.mark.parametrize("value", [[], [object()], "invalid"])
def test_rejects_non_tuple_input_boundary(value: object) -> None:
    with pytest.raises(TypeError, match="provenance_inputs must be a tuple"):
        explain_knowledge_provenance(_revision(), value)  # type: ignore[arg-type]
