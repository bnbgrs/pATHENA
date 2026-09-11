from __future__ import annotations

from uuid import UUID

import pytest

from athena.knowledge.concept_note_provenance import (
    ConceptNoteOrigin,
    ConceptNoteProvenance,
    ConceptNoteRevisionRef,
)


def _ref(entity: int, revision: int) -> ConceptNoteRevisionRef:
    return ConceptNoteRevisionRef(UUID(int=entity), UUID(int=revision))


def test_user_provenance_requires_real_actor_and_inputs() -> None:
    provenance = ConceptNoteProvenance(
        origin=ConceptNoteOrigin.USER,
        input_revisions=(_ref(1, 11), _ref(2, 22)),
        user_actor_id=UUID(int=99),
    )

    assert provenance.user_actor_id == UUID(int=99)
    assert provenance.input_revisions == (_ref(1, 11), _ref(2, 22))


def test_user_provenance_rejects_model_metadata() -> None:
    with pytest.raises(ValueError, match="must not claim model provenance"):
        ConceptNoteProvenance(
            origin=ConceptNoteOrigin.USER,
            input_revisions=(_ref(1, 11),),
            user_actor_id=UUID(int=99),
            model_signature_id=UUID(int=7),
        )


def test_model_provenance_requires_complete_model_chain() -> None:
    provenance = ConceptNoteProvenance(
        origin=ConceptNoteOrigin.MODEL,
        input_revisions=(_ref(1, 11),),
        model_signature_id=UUID(int=7),
        processing_run_id=UUID(int=8),
        pipeline_version="concept-note-v1",
    )

    assert provenance.model_signature_id == UUID(int=7)
    assert provenance.processing_run_id == UUID(int=8)


@pytest.mark.parametrize(
    ("model_signature_id", "processing_run_id", "pipeline_version"),
    [
        (None, UUID(int=8), "concept-note-v1"),
        (UUID(int=7), None, "concept-note-v1"),
        (UUID(int=7), UUID(int=8), "   "),
    ],
)
def test_model_provenance_fails_closed_when_chain_is_incomplete(
    model_signature_id: UUID | None,
    processing_run_id: UUID | None,
    pipeline_version: str | None,
) -> None:
    with pytest.raises(ValueError):
        ConceptNoteProvenance(
            origin=ConceptNoteOrigin.MODEL,
            input_revisions=(_ref(1, 11),),
            model_signature_id=model_signature_id,
            processing_run_id=processing_run_id,
            pipeline_version=pipeline_version,
        )


def test_provenance_rejects_missing_or_duplicate_input_revision_refs() -> None:
    with pytest.raises(ValueError, match="at least one input revision"):
        ConceptNoteProvenance(
            origin=ConceptNoteOrigin.USER,
            input_revisions=(),
            user_actor_id=UUID(int=99),
        )

    duplicate = _ref(1, 11)
    with pytest.raises(ValueError, match="must be unique"):
        ConceptNoteProvenance(
            origin=ConceptNoteOrigin.USER,
            input_revisions=(duplicate, duplicate),
            user_actor_id=UUID(int=99),
        )
