"""Canonical domain types for ATHENA Knowledge and Claims."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum


class KnowledgeKind(str, Enum):
    """Core v1 Knowledge kinds; storage remains text-extensible."""

    CONCEPT = "concept"
    FACT = "fact"
    DECISION = "decision"
    GOAL = "goal"
    IDEA = "idea"
    EXPERIENCE = "experience"
    PROCEDURE = "procedure"
    EVENT = "event"
    PROJECT_KNOWLEDGE = "project_knowledge"
    SUMMARY = "summary"
    OTHER = "other"


class ClaimKind(str, Enum):
    """Core v1 Claim kinds."""

    FACTUAL_ASSERTION = "factual_assertion"
    ATTRIBUTED_OPINION = "attributed_opinion"
    HYPOTHESIS = "hypothesis"
    DECISION = "decision"
    INTENTION = "intention"
    DEFINITION = "definition"
    OBSERVATION = "observation"
    EVENT_ASSERTION = "event_assertion"
    USER_STATEMENT = "user_statement"
    OTHER = "other"


class EpistemicStatus(str, Enum):
    """Versionable epistemic state; deliberately not a truth boolean."""

    ASSERTED = "asserted"
    SUPPORTED = "supported"
    DISPUTED = "disputed"
    CONTRADICTED = "contradicted"
    RETRACTED = "retracted"
    SUPERSEDED = "superseded"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"


class EvidenceRole(str, Enum):
    """Semantic role of an evidence link."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MENTIONS = "mentions"
    CONTEXTUALIZES = "contextualizes"
    ORIGINATES = "originates"


def _require_uuid(value: object, *, field_name: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{field_name} must be a UUID.")
    return value


def _require_optional_uuid(value: object, *, field_name: str) -> uuid.UUID | None:
    if value is None:
        return None
    return _require_uuid(value, field_name=field_name)


def _require_nonnegative_int(value: object, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")
    return value


def _require_optional_timestamp(value: object, *, field_name: str) -> int | None:
    if value is None:
        return None
    return _require_nonnegative_int(value, field_name=field_name)


def _validate_temporal_range(valid_from_us: int | None, valid_to_us: int | None) -> None:
    start = _require_optional_timestamp(valid_from_us, field_name="valid_from_us")
    end = _require_optional_timestamp(valid_to_us, field_name="valid_to_us")
    if start is not None and end is not None and end < start:
        raise ValueError("valid_to_us must be greater than or equal to valid_from_us.")


def _require_meaningful_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")
    return normalized


def _normalize_optional_text(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text or None.")
    normalized = value.strip()
    return normalized or None


@dataclass(frozen=True, slots=True)
class KnowledgeUnitDraft:
    """Unprotected canonical KnowledgeUnit content proposed for one revision."""

    knowledge_kind: KnowledgeKind
    body: str
    title: str | None = None
    valid_from_us: int | None = None
    valid_to_us: int | None = None
    epistemic_status: EpistemicStatus = EpistemicStatus.ASSERTED

    def __post_init__(self) -> None:
        if not isinstance(self.knowledge_kind, KnowledgeKind):
            raise TypeError("knowledge_kind must be a KnowledgeKind.")
        if not isinstance(self.epistemic_status, EpistemicStatus):
            raise TypeError("epistemic_status must be an EpistemicStatus.")
        object.__setattr__(
            self,
            "body",
            _require_meaningful_text(self.body, field_name="body"),
        )
        object.__setattr__(
            self,
            "title",
            _normalize_optional_text(self.title, field_name="title"),
        )
        _validate_temporal_range(self.valid_from_us, self.valid_to_us)


@dataclass(frozen=True, slots=True)
class ClaimDraft:
    """Unprotected Claim content proposed for one canonical revision."""

    claim_kind: ClaimKind
    statement: str
    epistemic_status: EpistemicStatus = EpistemicStatus.ASSERTED
    subject_entity_id: uuid.UUID | None = None
    predicate: str | None = None
    object_entity_id: uuid.UUID | None = None
    attributed_to_entity_id: uuid.UUID | None = None
    valid_from_us: int | None = None
    valid_to_us: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.claim_kind, ClaimKind):
            raise TypeError("claim_kind must be a ClaimKind.")
        if not isinstance(self.epistemic_status, EpistemicStatus):
            raise TypeError("epistemic_status must be an EpistemicStatus.")
        _require_optional_uuid(self.subject_entity_id, field_name="subject_entity_id")
        _require_optional_uuid(self.object_entity_id, field_name="object_entity_id")
        _require_optional_uuid(
            self.attributed_to_entity_id,
            field_name="attributed_to_entity_id",
        )
        object.__setattr__(
            self,
            "statement",
            _require_meaningful_text(self.statement, field_name="statement"),
        )
        object.__setattr__(
            self,
            "predicate",
            _normalize_optional_text(self.predicate, field_name="predicate"),
        )
        _validate_temporal_range(self.valid_from_us, self.valid_to_us)

        if self.claim_kind is ClaimKind.ATTRIBUTED_OPINION and self.attributed_to_entity_id is None:
            raise ValueError("Attributed opinions require attributed_to_entity_id.")


@dataclass(frozen=True, slots=True)
class KnowledgeUnitRevision:
    knowledge_id: uuid.UUID
    revision_id: uuid.UUID
    revision_no: int
    created_at_us: int
    created_by_actor_id: uuid.UUID
    provenance_id: uuid.UUID
    payload: KnowledgeUnitDraft

    def __post_init__(self) -> None:
        _require_uuid(self.knowledge_id, field_name="knowledge_id")
        _require_uuid(self.revision_id, field_name="revision_id")
        _require_uuid(self.created_by_actor_id, field_name="created_by_actor_id")
        _require_uuid(self.provenance_id, field_name="provenance_id")
        revision_no = _require_nonnegative_int(self.revision_no, field_name="revision_no")
        if revision_no < 1:
            raise ValueError("revision_no must be at least 1.")
        _require_nonnegative_int(self.created_at_us, field_name="created_at_us")
        if not isinstance(self.payload, KnowledgeUnitDraft):
            raise TypeError("payload must be a KnowledgeUnitDraft.")


@dataclass(frozen=True, slots=True)
class KnowledgeUnitSnapshot:
    """Current canonical state of one stable KnowledgeUnit entity."""

    knowledge_id: uuid.UUID
    lifecycle_state: str
    revision: KnowledgeUnitRevision

    def __post_init__(self) -> None:
        _require_uuid(self.knowledge_id, field_name="knowledge_id")
        _require_meaningful_text(self.lifecycle_state, field_name="lifecycle_state")
        if not isinstance(self.revision, KnowledgeUnitRevision):
            raise TypeError("revision must be a KnowledgeUnitRevision.")
        if self.revision.knowledge_id != self.knowledge_id:
            raise ValueError("Knowledge snapshot revision belongs to a different entity.")


@dataclass(frozen=True, slots=True)
class ProvenanceInputRef:
    """Stable input reference that explains one semantic revision."""

    provenance_id: uuid.UUID
    input_entity_id: uuid.UUID
    input_revision_id: uuid.UUID | None
    input_role: str
    ordinal: int

    def __post_init__(self) -> None:
        _require_uuid(self.provenance_id, field_name="provenance_id")
        _require_uuid(self.input_entity_id, field_name="input_entity_id")
        _require_optional_uuid(self.input_revision_id, field_name="input_revision_id")
        _require_nonnegative_int(self.ordinal, field_name="ordinal")
        object.__setattr__(
            self,
            "input_role",
            _require_meaningful_text(self.input_role, field_name="input_role"),
        )


@dataclass(frozen=True, slots=True)
class ClaimRevision:
    claim_id: uuid.UUID
    revision_id: uuid.UUID
    revision_no: int
    created_at_us: int
    created_by_actor_id: uuid.UUID
    provenance_id: uuid.UUID
    payload: ClaimDraft

    def __post_init__(self) -> None:
        _require_uuid(self.claim_id, field_name="claim_id")
        _require_uuid(self.revision_id, field_name="revision_id")
        _require_uuid(self.created_by_actor_id, field_name="created_by_actor_id")
        _require_uuid(self.provenance_id, field_name="provenance_id")
        revision_no = _require_nonnegative_int(self.revision_no, field_name="revision_no")
        if revision_no < 1:
            raise ValueError("revision_no must be at least 1.")
        _require_nonnegative_int(self.created_at_us, field_name="created_at_us")
        if not isinstance(self.payload, ClaimDraft):
            raise TypeError("payload must be a ClaimDraft.")


@dataclass(frozen=True, slots=True)
class ClaimSnapshot:
    """Current canonical state of one stable Claim entity."""

    claim_id: uuid.UUID
    lifecycle_state: str
    revision: ClaimRevision

    def __post_init__(self) -> None:
        _require_uuid(self.claim_id, field_name="claim_id")
        _require_meaningful_text(self.lifecycle_state, field_name="lifecycle_state")
        if not isinstance(self.revision, ClaimRevision):
            raise TypeError("revision must be a ClaimRevision.")
        if self.revision.claim_id != self.claim_id:
            raise ValueError("Claim snapshot revision belongs to a different entity.")


@dataclass(frozen=True, slots=True)
class ClaimEvidenceRef:
    """One concrete evidence reference for a Claim."""

    evidence_role: EvidenceRole
    provenance_id: uuid.UUID
    anchor_id: uuid.UUID | None = None
    message_id: uuid.UUID | None = None
    evidence_entity_id: uuid.UUID | None = None
    evidence_revision_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_role, EvidenceRole):
            raise TypeError("evidence_role must be an EvidenceRole.")
        _require_uuid(self.provenance_id, field_name="provenance_id")
        _require_optional_uuid(self.anchor_id, field_name="anchor_id")
        _require_optional_uuid(self.message_id, field_name="message_id")
        _require_optional_uuid(self.evidence_entity_id, field_name="evidence_entity_id")
        _require_optional_uuid(self.evidence_revision_id, field_name="evidence_revision_id")
        if not any(
            (
                self.anchor_id,
                self.message_id,
                self.evidence_entity_id,
                self.evidence_revision_id,
            )
        ):
            raise ValueError("Claim evidence requires at least one concrete evidence reference.")
