from __future__ import annotations

import uuid

import pytest

from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemorySensitivity,
    ModelInferredMemoryProposal,
    PersonalMemoryDraft,
)


def _draft() -> PersonalMemoryDraft:
    return PersonalMemoryDraft(
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
        content="Prefer concise summaries.",
        learning_mode=MemoryLearningMode.MODEL_INFERRED,
        sensitivity=MemorySensitivity.NORMAL,
        confidence=0.9,
    )


@pytest.mark.parametrize("field_name", ["model_signature_id", "processing_run_id"])
def test_model_inferred_proposal_rejects_non_uuid_provenance(field_name: str) -> None:
    values: dict[str, object] = {
        "draft": _draft(),
        "model_signature_id": uuid.uuid4(),
        "processing_run_id": uuid.uuid4(),
    }
    values[field_name] = str(uuid.uuid4())

    with pytest.raises(TypeError, match="requires UUID"):
        ModelInferredMemoryProposal(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("review_required", [1, "true", None])
def test_model_inferred_proposal_requires_exact_true_review_gate(review_required: object) -> None:
    with pytest.raises(ValueError, match="must remain review-gated"):
        ModelInferredMemoryProposal(
            draft=_draft(),
            model_signature_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            review_required=review_required,  # type: ignore[arg-type]
        )


def test_model_inferred_proposal_accepts_real_uuid_provenance_and_true_review_gate() -> None:
    model_signature_id = uuid.uuid4()
    processing_run_id = uuid.uuid4()

    proposal = ModelInferredMemoryProposal(
        draft=_draft(),
        model_signature_id=model_signature_id,
        processing_run_id=processing_run_id,
        review_required=True,
    )

    assert proposal.model_signature_id == model_signature_id
    assert proposal.processing_run_id == processing_run_id
    assert proposal.review_required is True