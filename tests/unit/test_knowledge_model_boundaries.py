from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import (
    ClaimDraft,
    ClaimEvidenceRef,
    ClaimKind,
    ClaimRevision,
    ClaimSnapshot,
    EpistemicStatus,
    EvidenceRole,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
    ProvenanceInputRef,
)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def test_knowledge_draft_rejects_non_enum_and_bool_timestamp() -> None:
    with pytest.raises(TypeError, match="knowledge_kind"):
        KnowledgeUnitDraft(  # type: ignore[arg-type]
            knowledge_kind="fact",
            body="body",
        )
    with pytest.raises(TypeError, match="valid_from_us"):
        KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            body="body",
            valid_from_us=True,  # type: ignore[arg-type]
        )


def test_claim_draft_rejects_invalid_uuid_and_temporal_range() -> None:
    with pytest.raises(TypeError, match="subject_entity_id"):
        ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement="statement",
            subject_entity_id="bad",  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="valid_to_us"):
        ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement="statement",
            valid_from_us=20,
            valid_to_us=10,
        )


def test_revision_rejects_bool_revision_number() -> None:
    with pytest.raises(TypeError, match="revision_no"):
        KnowledgeUnitRevision(
            knowledge_id=_uuid(),
            revision_id=_uuid(),
            revision_no=True,  # type: ignore[arg-type]
            created_at_us=1,
            created_by_actor_id=_uuid(),
            provenance_id=_uuid(),
            payload=KnowledgeUnitDraft(
                knowledge_kind=KnowledgeKind.FACT,
                body="body",
            ),
        )


def test_knowledge_snapshot_requires_matching_entity() -> None:
    revision = KnowledgeUnitRevision(
        knowledge_id=_uuid(),
        revision_id=_uuid(),
        revision_no=1,
        created_at_us=1,
        created_by_actor_id=_uuid(),
        provenance_id=_uuid(),
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            body="body",
        ),
    )
    with pytest.raises(ValueError, match="different entity"):
        KnowledgeUnitSnapshot(
            knowledge_id=_uuid(),
            lifecycle_state="active",
            revision=revision,
        )


def test_claim_snapshot_requires_matching_entity() -> None:
    revision = ClaimRevision(
        claim_id=_uuid(),
        revision_id=_uuid(),
        revision_no=1,
        created_at_us=1,
        created_by_actor_id=_uuid(),
        provenance_id=_uuid(),
        payload=ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement="statement",
            epistemic_status=EpistemicStatus.ASSERTED,
        ),
    )
    with pytest.raises(ValueError, match="different entity"):
        ClaimSnapshot(
            claim_id=_uuid(),
            lifecycle_state="active",
            revision=revision,
        )


def test_provenance_input_rejects_bool_ordinal() -> None:
    with pytest.raises(TypeError, match="ordinal"):
        ProvenanceInputRef(
            provenance_id=_uuid(),
            input_entity_id=_uuid(),
            input_revision_id=None,
            input_role="source",
            ordinal=False,  # type: ignore[arg-type]
        )


def test_claim_evidence_requires_typed_reference() -> None:
    with pytest.raises(TypeError, match="anchor_id"):
        ClaimEvidenceRef(
            evidence_role=EvidenceRole.SUPPORTS,
            provenance_id=_uuid(),
            anchor_id="bad",  # type: ignore[arg-type]
        )


def test_valid_claim_evidence_is_accepted() -> None:
    evidence = ClaimEvidenceRef(
        evidence_role=EvidenceRole.SUPPORTS,
        provenance_id=_uuid(),
        anchor_id=_uuid(),
    )
    assert evidence.anchor_id is not None
