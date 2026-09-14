from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import (
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
)
from athena.knowledge.project_membership import plan_project_memberships
from athena.knowledge.relation_registry import (
    RelationDirection,
    RelationTypeDefinition,
    RelationTypeRegistry,
)


def _snapshot(kind: KnowledgeKind) -> KnowledgeUnitSnapshot:
    knowledge_id = uuid.uuid4()
    return KnowledgeUnitSnapshot(
        knowledge_id=knowledge_id,
        lifecycle_state="active",
        revision=KnowledgeUnitRevision(
            knowledge_id=knowledge_id,
            revision_id=uuid.uuid4(),
            revision_no=1,
            created_at_us=1,
            created_by_actor_id=uuid.uuid4(),
            provenance_id=uuid.uuid4(),
            payload=KnowledgeUnitDraft(
                knowledge_kind=kind,
                body=f"{kind.value} body",
            ),
        ),
    )


def test_plans_multiple_project_memberships_without_collapsing_targets() -> None:
    source = _snapshot(KnowledgeKind.FACT)
    first = _snapshot(KnowledgeKind.PROJECT_KNOWLEDGE)
    second = _snapshot(KnowledgeKind.PROJECT_KNOWLEDGE)

    plan = plan_project_memberships(source=source, projects=(first, second))

    assert plan.source_entity_id == source.knowledge_id
    assert tuple(edge.target_entity_id for edge in plan.edges) == (
        first.knowledge_id,
        second.knowledge_id,
    )
    assert all(edge.relation_type == "belongs_to_project" for edge in plan.edges)


def test_duplicate_project_memberships_collapse_in_first_seen_order() -> None:
    source = _snapshot(KnowledgeKind.FACT)
    project = _snapshot(KnowledgeKind.PROJECT_KNOWLEDGE)

    plan = plan_project_memberships(source=source, projects=(project, project))

    assert len(plan.edges) == 1
    assert plan.edges[0].target_entity_id == project.knowledge_id


def test_non_project_target_is_rejected() -> None:
    with pytest.raises(ValueError, match="PROJECT_KNOWLEDGE"):
        plan_project_memberships(
            source=_snapshot(KnowledgeKind.FACT),
            projects=(_snapshot(KnowledgeKind.FACT),),
        )


def test_empty_project_set_is_rejected() -> None:
    with pytest.raises(ValueError, match="At least one project"):
        plan_project_memberships(source=_snapshot(KnowledgeKind.FACT), projects=())


def test_wrong_project_collection_type_fails_closed() -> None:
    project = _snapshot(KnowledgeKind.PROJECT_KNOWLEDGE)
    with pytest.raises(TypeError, match="tuple"):
        plan_project_memberships(
            source=_snapshot(KnowledgeKind.FACT),
            projects=[project],  # type: ignore[arg-type]
        )


def test_registry_cannot_silently_fallback_membership_semantics() -> None:
    registry = RelationTypeRegistry(
        definitions=(
            RelationTypeDefinition(
                name="related_to",
                direction=RelationDirection.SYMMETRIC,
                semantics="Fallback only.",
            ),
        )
    )
    with pytest.raises(RuntimeError, match="unavailable"):
        plan_project_memberships(
            source=_snapshot(KnowledgeKind.FACT),
            projects=(_snapshot(KnowledgeKind.PROJECT_KNOWLEDGE),),
            registry=registry,
        )
