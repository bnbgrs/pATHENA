"""Truthful explanations of how one Knowledge revision changed from its predecessor."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from athena.knowledge.models import KnowledgeUnitRevision

RevisionValue = str | int | None


@dataclass(frozen=True, slots=True)
class RevisionFieldChange:
    """One payload field whose recorded value changed between two revisions."""

    field: str
    previous: RevisionValue
    current: RevisionValue


@dataclass(frozen=True, slots=True)
class KnowledgeRevisionChangeExplanation:
    """Transport-neutral answer to "why did this change?" for adjacent revisions."""

    knowledge_id: uuid.UUID
    previous_revision_id: uuid.UUID
    current_revision_id: uuid.UUID
    previous_revision_no: int
    current_revision_no: int
    changed_by_actor_id: uuid.UUID
    changed_at_us: int
    recorded_reason: str | None
    changes: tuple[RevisionFieldChange, ...]
    text: str


def explain_knowledge_revision_change(
    previous: KnowledgeUnitRevision,
    current: KnowledgeUnitRevision,
    *,
    recorded_reason: str | None = None,
) -> KnowledgeRevisionChangeExplanation:
    """Explain an adjacent revision transition using only supplied recorded facts."""
    if not isinstance(previous, KnowledgeUnitRevision):
        raise TypeError("previous must be a KnowledgeUnitRevision.")
    if not isinstance(current, KnowledgeUnitRevision):
        raise TypeError("current must be a KnowledgeUnitRevision.")
    if previous.knowledge_id != current.knowledge_id:
        raise ValueError("Revisions must belong to the same KnowledgeUnit.")
    if current.revision_no != previous.revision_no + 1:
        raise ValueError("current must be the direct successor of previous.")
    if current.revision_id == previous.revision_id:
        raise ValueError("Adjacent revisions must have distinct revision IDs.")
    if current.created_at_us < previous.created_at_us:
        raise ValueError("current revision timestamp must not precede previous.")

    reason = _normalize_reason(recorded_reason)
    changes = _payload_changes(previous, current)
    changed_at = datetime.fromtimestamp(current.created_at_us / 1_000_000, tz=UTC).isoformat()
    fields = ", ".join(change.field for change in changes)
    change_text = f"Changed payload fields: {fields}." if changes else "No payload fields changed."
    reason_text = (
        f"Recorded reason: {reason}."
        if reason is not None
        else "No recorded reason was supplied to this explanation."
    )
    text = (
        f"Knowledge revision {current.revision_no} replaced revision {previous.revision_no} "
        f"at {changed_at} by actor {current.created_by_actor_id}. {reason_text} {change_text}"
    )

    return KnowledgeRevisionChangeExplanation(
        knowledge_id=current.knowledge_id,
        previous_revision_id=previous.revision_id,
        current_revision_id=current.revision_id,
        previous_revision_no=previous.revision_no,
        current_revision_no=current.revision_no,
        changed_by_actor_id=current.created_by_actor_id,
        changed_at_us=current.created_at_us,
        recorded_reason=reason,
        changes=changes,
        text=text,
    )


def _normalize_reason(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("recorded_reason must be text or None.")
    normalized = value.strip()
    return normalized or None


def _payload_changes(
    previous: KnowledgeUnitRevision,
    current: KnowledgeUnitRevision,
) -> tuple[RevisionFieldChange, ...]:
    before = previous.payload
    after = current.payload
    candidates: tuple[tuple[str, RevisionValue, RevisionValue], ...] = (
        ("knowledge_kind", before.knowledge_kind.value, after.knowledge_kind.value),
        ("title", before.title, after.title),
        ("body", before.body, after.body),
        ("valid_from_us", before.valid_from_us, after.valid_from_us),
        ("valid_to_us", before.valid_to_us, after.valid_to_us),
        ("epistemic_status", before.epistemic_status.value, after.epistemic_status.value),
    )
    return tuple(
        RevisionFieldChange(field=field, previous=old, current=new)
        for field, old, new in candidates
        if old != new
    )
