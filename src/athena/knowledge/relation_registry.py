"""Versioned relation-type registry and deterministic edge canonicalization."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

RELATION_REGISTRY_VERSION = "beta-0.1"


class RelationDirection(str, Enum):
    """Direction semantics for one registered relation type."""

    DIRECTED = "directed"
    SYMMETRIC = "symmetric"


@dataclass(frozen=True, slots=True)
class RelationTypeDefinition:
    """One curated relation type in the versioned Core registry."""

    name: str
    direction: RelationDirection
    semantics: str
    allowed_domain_pairs: tuple[tuple[str, str], ...] = ()
    inverse_name: str | None = None
    deprecated: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Relation type name must be non-empty.")
        if not self.semantics.strip():
            raise ValueError("Relation type semantics must be non-empty.")
        if self.inverse_name is not None and not self.inverse_name.strip():
            raise ValueError("Inverse relation name must be non-empty when provided.")
        for source_domain, target_domain in self.allowed_domain_pairs:
            if not source_domain.strip() or not target_domain.strip():
                raise ValueError("Allowed relation domains must be non-empty.")

    def allows_domains(self, source_domain: str, target_domain: str) -> bool:
        """Return whether this definition permits the requested domain pair."""
        if not source_domain.strip() or not target_domain.strip():
            raise ValueError("Relation domains must be non-empty.")
        if not self.allowed_domain_pairs:
            return True
        pair = (source_domain, target_domain)
        if pair in self.allowed_domain_pairs:
            return True
        if self.direction is RelationDirection.SYMMETRIC:
            return (target_domain, source_domain) in self.allowed_domain_pairs
        return False


@dataclass(frozen=True, slots=True)
class CanonicalRelationEdge:
    """A registry-resolved relation edge with deterministic endpoint ordering."""

    relation_type: str
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID


_DEFAULT_RELATION_TYPES = (
    RelationTypeDefinition(
        name="related_to",
        direction=RelationDirection.SYMMETRIC,
        semantics="The entities are semantically related without asserting identity.",
    ),
    RelationTypeDefinition(
        name="same_as",
        direction=RelationDirection.SYMMETRIC,
        semantics="The entities represent the same semantic identity.",
    ),
    RelationTypeDefinition(
        name="different_from",
        direction=RelationDirection.SYMMETRIC,
        semantics="The entities are explicitly distinct semantic identities.",
    ),
    RelationTypeDefinition(
        name="belongs_to_project",
        direction=RelationDirection.DIRECTED,
        semantics="The source entity is assigned to the target project.",
        allowed_domain_pairs=(("knowledge", "project"),),
    ),
)


class RelationTypeRegistry:
    """Curated Core registry that prevents ad-hoc relation-type proliferation."""

    def __init__(
        self,
        definitions: tuple[RelationTypeDefinition, ...] = _DEFAULT_RELATION_TYPES,
        *,
        fallback_name: str = "related_to",
        version: str = RELATION_REGISTRY_VERSION,
    ) -> None:
        if not version.strip():
            raise ValueError("Relation registry version must be non-empty.")
        by_name: dict[str, RelationTypeDefinition] = {}
        for definition in definitions:
            if definition.name in by_name:
                raise ValueError(f"Duplicate relation type: {definition.name}")
            by_name[definition.name] = definition
        if fallback_name not in by_name:
            raise ValueError("Fallback relation type must exist in the registry.")
        if by_name[fallback_name].deprecated:
            raise ValueError("Fallback relation type cannot be deprecated.")
        self._definitions = by_name
        self._fallback_name = fallback_name
        self.version = version

    def definitions(self) -> tuple[RelationTypeDefinition, ...]:
        """Return registry definitions in stable insertion order."""
        return tuple(self._definitions.values())

    def definition(self, name: str) -> RelationTypeDefinition:
        """Resolve a requested type, falling back instead of inventing ontology."""
        requested = name.strip()
        if not requested:
            raise ValueError("Relation type name must be non-empty.")
        definition = self._definitions.get(requested)
        if definition is None or definition.deprecated:
            return self._definitions[self._fallback_name]
        return definition

    def canonicalize(
        self,
        *,
        relation_type: str,
        source_entity_id: uuid.UUID,
        target_entity_id: uuid.UUID,
    ) -> CanonicalRelationEdge:
        """Resolve type and deterministically order symmetric relation endpoints."""
        if not isinstance(source_entity_id, uuid.UUID):
            raise TypeError("source_entity_id must be a UUID.")
        if not isinstance(target_entity_id, uuid.UUID):
            raise TypeError("target_entity_id must be a UUID.")
        definition = self.definition(relation_type)
        source = source_entity_id
        target = target_entity_id
        if (
            definition.direction is RelationDirection.SYMMETRIC
            and target.bytes < source.bytes
        ):
            source, target = target, source
        return CanonicalRelationEdge(
            relation_type=definition.name,
            source_entity_id=source,
            target_entity_id=target,
        )
