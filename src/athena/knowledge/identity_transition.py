from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MergeTransition:
    """Validated semantic identity transition for a KnowledgeUnit merge.

    The transition is descriptive only: it does not persist, delete, or invent
    revisions. Callers must supply identities that already belong to the
    canonical knowledge workflow.
    """

    source_entity_ids: tuple[UUID, ...]
    result_entity_id: UUID

    def __post_init__(self) -> None:
        if len(self.source_entity_ids) < 2:
            raise ValueError("merge requires at least two source entities")
        if len(set(self.source_entity_ids)) != len(self.source_entity_ids):
            raise ValueError("merge source entities must be unique")

    @property
    def superseded_entity_ids(self) -> tuple[UUID, ...]:
        """Return source identities no longer preferred after the merge."""
        return tuple(
            entity_id
            for entity_id in self.source_entity_ids
            if entity_id != self.result_entity_id
        )

    @property
    def reuses_existing_identity(self) -> bool:
        return self.result_entity_id in self.source_entity_ids


@dataclass(frozen=True, slots=True)
class SplitTransition:
    """Validated semantic identity transition for a KnowledgeUnit split.

    A split creates independently addressable identities and preserves the
    original identity as historical/superseded state. Persistence remains the
    responsibility of the canonical knowledge service.
    """

    source_entity_id: UUID
    result_entity_ids: tuple[UUID, ...]

    def __post_init__(self) -> None:
        if len(self.result_entity_ids) < 2:
            raise ValueError("split requires at least two result entities")
        if len(set(self.result_entity_ids)) != len(self.result_entity_ids):
            raise ValueError("split result entities must be unique")
        if self.source_entity_id in self.result_entity_ids:
            raise ValueError("split result entities must use new identities")

    @property
    def superseded_entity_ids(self) -> tuple[UUID, ...]:
        return (self.source_entity_id,)
