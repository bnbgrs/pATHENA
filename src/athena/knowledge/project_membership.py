"""Deterministic Core planning for Knowledge-to-Project membership edges."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.knowledge.models import KnowledgeKind, KnowledgeUnitSnapshot
from athena.knowledge.relation_registry import (
    CanonicalRelationEdge,
    RelationTypeRegistry,
)


@dataclass(frozen=True, slots=True)
class ProjectMembershipPlan:
    """Canonical membership edges for one Knowledge entity."""

    source_entity_id: uuid.UUID
    edges: tuple[CanonicalRelationEdge, ...]


def plan_project_memberships(
    *,
    source: KnowledgeUnitSnapshot,
    projects: tuple[KnowledgeUnitSnapshot, ...],
    registry: RelationTypeRegistry | None = None,
) -> ProjectMembershipPlan:
    """Plan one-or-more ``belongs_to_project`` edges without persisting them.

    Callers must pass canonical Knowledge snapshots. Project targets are required
    to use the established ``project_knowledge`` kind. Duplicate targets collapse
    to one edge while preserving first-seen order, so one Knowledge entity can
    safely belong to multiple projects without inventing identities or relations.
    """
    if not isinstance(source, KnowledgeUnitSnapshot):
        raise TypeError("source must be a KnowledgeUnitSnapshot.")
    if not isinstance(projects, tuple):
        raise TypeError("projects must be a tuple of KnowledgeUnitSnapshot values.")
    if not projects:
        raise ValueError("At least one project is required for membership planning.")

    relation_registry = registry or RelationTypeRegistry()
    definition = relation_registry.definition("belongs_to_project")
    if definition.name != "belongs_to_project" or definition.deprecated:
        raise RuntimeError(
            "belongs_to_project is unavailable in the relation registry."
        )
    if not definition.allows_domains("knowledge", "project"):
        raise RuntimeError(
            "belongs_to_project does not permit Knowledge-to-Project edges."
        )

    edges: list[CanonicalRelationEdge] = []
    seen_project_ids: set[uuid.UUID] = set()
    for project in projects:
        if not isinstance(project, KnowledgeUnitSnapshot):
            raise TypeError("projects must contain only KnowledgeUnitSnapshot values.")
        if (
            project.revision.payload.knowledge_kind
            is not KnowledgeKind.PROJECT_KNOWLEDGE
        ):
            raise ValueError(
                "Project targets must use KnowledgeKind.PROJECT_KNOWLEDGE."
            )
        if project.knowledge_id in seen_project_ids:
            continue
        seen_project_ids.add(project.knowledge_id)
        edge = relation_registry.canonicalize(
            relation_type="belongs_to_project",
            source_entity_id=source.knowledge_id,
            target_entity_id=project.knowledge_id,
        )
        if (
            edge.relation_type != "belongs_to_project"
            or edge.source_entity_id != source.knowledge_id
            or edge.target_entity_id != project.knowledge_id
        ):
            raise RuntimeError(
                "Relation registry changed project membership semantics."
            )
        edges.append(edge)

    return ProjectMembershipPlan(
        source_entity_id=source.knowledge_id,
        edges=tuple(edges),
    )
