from __future__ import annotations

import uuid

import pytest

from athena.knowledge.relation_registry import (
    RelationDirection,
    RelationTypeDefinition,
    RelationTypeRegistry,
)


def test_unknown_relation_type_falls_back_without_ontology_growth() -> None:
    registry = RelationTypeRegistry()

    resolved = registry.definition("model_invented_relation")

    assert resolved.name == "related_to"
    assert tuple(item.name for item in registry.definitions()) == (
        "related_to",
        "same_as",
        "different_from",
        "belongs_to_project",
    )


def test_symmetric_relation_has_one_deterministic_edge_representation() -> None:
    registry = RelationTypeRegistry()
    low = uuid.UUID(int=1)
    high = uuid.UUID(int=2)

    forward = registry.canonicalize(
        relation_type="related_to",
        source_entity_id=low,
        target_entity_id=high,
    )
    reverse = registry.canonicalize(
        relation_type="related_to",
        source_entity_id=high,
        target_entity_id=low,
    )

    assert forward == reverse
    assert forward.source_entity_id == low
    assert forward.target_entity_id == high


def test_directed_relation_preserves_semantic_direction() -> None:
    registry = RelationTypeRegistry()
    knowledge_id = uuid.UUID(int=2)
    project_id = uuid.UUID(int=1)

    edge = registry.canonicalize(
        relation_type="belongs_to_project",
        source_entity_id=knowledge_id,
        target_entity_id=project_id,
    )

    assert edge.source_entity_id == knowledge_id
    assert edge.target_entity_id == project_id
    assert edge.relation_type == "belongs_to_project"


def test_domain_constraints_respect_direction_and_symmetry() -> None:
    directed = RelationTypeDefinition(
        name="belongs_to_project",
        direction=RelationDirection.DIRECTED,
        semantics="Membership edge.",
        allowed_domain_pairs=(("knowledge", "project"),),
    )
    symmetric = RelationTypeDefinition(
        name="peer",
        direction=RelationDirection.SYMMETRIC,
        semantics="Peer relation.",
        allowed_domain_pairs=(("claim", "knowledge"),),
    )

    assert directed.allows_domains("knowledge", "project") is True
    assert directed.allows_domains("project", "knowledge") is False
    assert symmetric.allows_domains("claim", "knowledge") is True
    assert symmetric.allows_domains("knowledge", "claim") is True


def test_registry_rejects_duplicate_relation_names() -> None:
    definition = RelationTypeDefinition(
        name="related_to",
        direction=RelationDirection.SYMMETRIC,
        semantics="Fallback relation.",
    )

    with pytest.raises(ValueError, match="Duplicate relation type"):
        RelationTypeRegistry((definition, definition))
