"""Deterministic supersession-edge planning for canonical Knowledge identities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.knowledge.relation_registry import (
    CanonicalRelationEdge,
    RelationTypeRegistry,
)


class KnowledgeSupersessionPlanError(ValueError):
    """Raised when a supersession plan violates canonical identity rules."""


@dataclass(frozen=True, slots=True)
class KnowledgeSupersessionPlan:
    """Directed historical-to-successor edges for one semantic transition."""

    superseded_entity_ids: tuple[uuid.UUID, ...]
    successor_entity_id: uuid.UUID
    edges: tuple[CanonicalRelationEdge, ...]


def plan_knowledge_supersession(
    *,
    superseded_entity_ids: tuple[uuid.UUID, ...],
    successor_entity_id: uuid.UUID,
    registry: RelationTypeRegistry | None = None,
) -> KnowledgeSupersessionPlan:
    """Plan ``superseded_by`` edges without mutating or deleting Knowledge history.

    This planner consumes identity consequences already authorized by a merge,
    split, correction, or other semantic workflow. It deliberately performs no
    persistence. Repositories can later write the returned directed edges inside
    their existing atomic transaction and audit boundaries.
    """
    if not isinstance(superseded_entity_ids, tuple):
        raise TypeError("superseded_entity_ids must be a tuple of UUIDs.")
    if not superseded_entity_ids:
        raise KnowledgeSupersessionPlanError(
            "At least one superseded Knowledge identity is required."
        )
    if not isinstance(successor_entity_id, uuid.UUID):
        raise TypeError("successor_entity_id must be a UUID.")

    normalized: list[uuid.UUID] = []
    for entity_id in superseded_entity_ids:
        if not isinstance(entity_id, uuid.UUID):
            raise TypeError("superseded_entity_ids must contain only UUID values.")
        normalized.append(entity_id)
    if len(set(normalized)) != len(normalized):
        raise KnowledgeSupersessionPlanError(
            "Superseded Knowledge identities must be unique."
        )
    if successor_entity_id in normalized:
        raise KnowledgeSupersessionPlanError(
            "A Knowledge identity cannot supersede itself."
        )

    relation_registry = registry or RelationTypeRegistry()
    definition = relation_registry.definition("superseded_by")
    if definition.name != "superseded_by" or definition.deprecated:
        raise RuntimeError("superseded_by is unavailable in the relation registry.")
    if not definition.allows_domains("knowledge", "knowledge"):
        raise RuntimeError(
            "superseded_by does not permit Knowledge-to-Knowledge edges."
        )

    edges: list[CanonicalRelationEdge] = []
    for source_entity_id in normalized:
        edge = relation_registry.canonicalize(
            relation_type="superseded_by",
            source_entity_id=source_entity_id,
            target_entity_id=successor_entity_id,
        )
        if (
            edge.relation_type != "superseded_by"
            or edge.source_entity_id != source_entity_id
            or edge.target_entity_id != successor_entity_id
        ):
            raise RuntimeError("Relation registry changed supersession semantics.")
        edges.append(edge)

    return KnowledgeSupersessionPlan(
        superseded_entity_ids=tuple(normalized),
        successor_entity_id=successor_entity_id,
        edges=tuple(edges),
    )
