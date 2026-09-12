"""Transport-neutral Knowledge revision history with derived payload diffs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

from athena.knowledge.models import KnowledgeUnitRevision
from athena.knowledge.revision_change_explanation import (
    RevisionValue,
    explain_knowledge_revision_change,
)


class KnowledgeHistoryReader(Protocol):
    """Minimal read boundary required by the revision-history API."""

    def history(self, knowledge_id: uuid.UUID) -> tuple[KnowledgeUnitRevision, ...]: ...


@dataclass(frozen=True, slots=True)
class KnowledgeHistoryFieldChangeResponse:
    field: str
    previous: RevisionValue
    current: RevisionValue


@dataclass(frozen=True, slots=True)
class KnowledgeHistoryEntryResponse:
    revision_id: str
    revision_no: int
    created_at_us: int
    actor_id: str
    changes_from_previous: tuple[KnowledgeHistoryFieldChangeResponse, ...]


@dataclass(frozen=True, slots=True)
class KnowledgeHistoryResponse:
    knowledge_id: str
    entries: tuple[KnowledgeHistoryEntryResponse, ...]


class KnowledgeHistoryApiService:
    """Expose immutable Knowledge history without inventing audit metadata."""

    def __init__(self, *, knowledge: KnowledgeHistoryReader) -> None:
        self._knowledge = knowledge

    def revision_history(self, knowledge_id: str) -> KnowledgeHistoryResponse:
        """Return recorded revisions plus an on-demand diff to each predecessor."""
        parsed_id = uuid.UUID(knowledge_id)
        revisions = self._knowledge.history(parsed_id)
        if not revisions:
            raise ValueError("Knowledge history must contain at least one revision.")

        entries: list[KnowledgeHistoryEntryResponse] = []
        previous: KnowledgeUnitRevision | None = None
        for index, revision in enumerate(revisions, start=1):
            if revision.knowledge_id != parsed_id:
                raise ValueError("Knowledge history contains a revision from another entity.")
            if revision.revision_no != index:
                raise ValueError("Knowledge history must be contiguous and start at revision 1.")

            changes: tuple[KnowledgeHistoryFieldChangeResponse, ...]
            if previous is None:
                changes = ()
            else:
                explanation = explain_knowledge_revision_change(previous, revision)
                changes = tuple(
                    KnowledgeHistoryFieldChangeResponse(
                        field=change.field,
                        previous=change.previous,
                        current=change.current,
                    )
                    for change in explanation.changes
                )

            entries.append(
                KnowledgeHistoryEntryResponse(
                    revision_id=str(revision.revision_id),
                    revision_no=revision.revision_no,
                    created_at_us=revision.created_at_us,
                    actor_id=str(revision.created_by_actor_id),
                    changes_from_previous=changes,
                )
            )
            previous = revision

        return KnowledgeHistoryResponse(
            knowledge_id=str(parsed_id),
            entries=tuple(entries),
        )
