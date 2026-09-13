"""Identity-preserving merge/split planning for canonical Knowledge entities.

The planner is deliberately persistence-neutral. It makes the identity and
supersession consequences explicit before repositories perform an atomic write,
so similarity scoring or transport code cannot silently erase historical IDs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


class KnowledgeIdentityPlanError(ValueError):
    """Raised when a merge/split request violates canonical identity rules."""


def _require_uuid(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")
    return value


def _require_uuid_tuple(value: object, label: str) -> tuple[uuid.UUID, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{label} must be a tuple of UUIDs.")
    return tuple(_require_uuid(item, f"{label} item") for item in value)


@dataclass(frozen=True, slots=True)
class KnowledgeMergePlan:
    """Identity consequences of one authorized semantic merge."""

    left_entity_id: uuid.UUID
    right_entity_id: uuid.UUID
    result_entity_id: uuid.UUID
    superseded_entity_ids: tuple[uuid.UUID, ...]

    @property
    def retains_existing_identity(self) -> bool:
        return self.result_entity_id in (
            self.left_entity_id,
            self.right_entity_id,
        )


@dataclass(frozen=True, slots=True)
class KnowledgeSplitPlan:
    """Identity consequences of splitting one canonical entity."""

    source_entity_id: uuid.UUID
    result_entity_ids: tuple[uuid.UUID, ...]
    superseded_entity_ids: tuple[uuid.UUID, ...]


def plan_knowledge_merge(
    *,
    left_entity_id: uuid.UUID,
    right_entity_id: uuid.UUID,
    result_entity_id: uuid.UUID,
) -> KnowledgeMergePlan:
    """Plan merge identity without deciding whether a semantic merge is justified.

    The caller must already have an authorized semantic merge decision. If the
    result keeps one existing identity, only the absorbed identity becomes
    superseded. If the result uses a new identity, both originals remain as
    superseded historical entities.
    """

    left = _require_uuid(left_entity_id, "left_entity_id")
    right = _require_uuid(right_entity_id, "right_entity_id")
    result = _require_uuid(result_entity_id, "result_entity_id")
    if left == right:
        raise KnowledgeIdentityPlanError(
            "A merge requires two distinct canonical entity IDs."
        )

    if result == left:
        superseded = (right,)
    elif result == right:
        superseded = (left,)
    else:
        superseded = (left, right)

    return KnowledgeMergePlan(
        left_entity_id=left,
        right_entity_id=right,
        result_entity_id=result,
        superseded_entity_ids=superseded,
    )


def plan_knowledge_split(
    *,
    source_entity_id: uuid.UUID,
    result_entity_ids: tuple[uuid.UUID, ...],
) -> KnowledgeSplitPlan:
    """Plan a split into independently addressable new canonical identities."""

    source = _require_uuid(source_entity_id, "source_entity_id")
    results = _require_uuid_tuple(result_entity_ids, "result_entity_ids")
    if len(results) < 2:
        raise KnowledgeIdentityPlanError(
            "A split requires at least two result entity IDs."
        )
    if len(set(results)) != len(results):
        raise KnowledgeIdentityPlanError(
            "Split result entity IDs must be unique."
        )
    if source in results:
        raise KnowledgeIdentityPlanError(
            "Split results must use new identities, not the source entity ID."
        )

    return KnowledgeSplitPlan(
        source_entity_id=source,
        result_entity_ids=results,
        superseded_entity_ids=(source,),
    )
