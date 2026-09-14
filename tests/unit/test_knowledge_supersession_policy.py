from __future__ import annotations

import uuid

import pytest

from athena.knowledge.relation_registry import (
    RelationDirection,
    RelationTypeDefinition,
    RelationTypeRegistry,
)
from athena.knowledge.supersession_policy import (
    KnowledgeSupersessionPlanError,
    plan_knowledge_supersession,
)


def test_default_registry_exposes_directed_knowledge_supersession() -> None:
    definition = RelationTypeRegistry().definition("superseded_by")

    assert definition.name == "superseded_by"
    assert definition.direction is RelationDirection.DIRECTED
    assert definition.allows_domains("knowledge", "knowledge")
    assert not definition.allows_domains("project", "knowledge")


def test_supersession_plan_preserves_source_order_and_direction() -> None:
    first = uuid.UUID(int=1)
    second = uuid.UUID(int=2)
    successor = uuid.UUID(int=3)

    plan = plan_knowledge_supersession(
        superseded_entity_ids=(first, second),
        successor_entity_id=successor,
    )

    assert plan.superseded_entity_ids == (first, second)
    assert plan.successor_entity_id == successor
    assert tuple(edge.relation_type for edge in plan.edges) == (
        "superseded_by",
        "superseded_by",
    )
    assert tuple(edge.source_entity_id for edge in plan.edges) == (first, second)
    assert tuple(edge.target_entity_id for edge in plan.edges) == (
        successor,
        successor,
    )


def test_supersession_plan_rejects_empty_duplicate_and_self_supersession() -> None:
    first = uuid.UUID(int=1)
    successor = uuid.UUID(int=2)

    with pytest.raises(KnowledgeSupersessionPlanError):
        plan_knowledge_supersession(
            superseded_entity_ids=(),
            successor_entity_id=successor,
        )
    with pytest.raises(KnowledgeSupersessionPlanError):
        plan_knowledge_supersession(
            superseded_entity_ids=(first, first),
            successor_entity_id=successor,
        )
    with pytest.raises(KnowledgeSupersessionPlanError):
        plan_knowledge_supersession(
            superseded_entity_ids=(successor,),
            successor_entity_id=successor,
        )


def test_supersession_plan_fails_closed_if_registry_would_fallback() -> None:
    registry = RelationTypeRegistry(
        definitions=(
            RelationTypeDefinition(
                name="related_to",
                direction=RelationDirection.SYMMETRIC,
                semantics="generic relation",
            ),
        )
    )

    with pytest.raises(RuntimeError, match="superseded_by is unavailable"):
        plan_knowledge_supersession(
            superseded_entity_ids=(uuid.UUID(int=1),),
            successor_entity_id=uuid.UUID(int=2),
            registry=registry,
        )


def test_supersession_plan_validates_uuid_types() -> None:
    with pytest.raises(TypeError):
        plan_knowledge_supersession(
            superseded_entity_ids=("not-a-uuid",),  # type: ignore[arg-type]
            successor_entity_id=uuid.UUID(int=2),
        )
    with pytest.raises(TypeError):
        plan_knowledge_supersession(
            superseded_entity_ids=(uuid.UUID(int=1),),
            successor_entity_id="not-a-uuid",  # type: ignore[arg-type]
        )
