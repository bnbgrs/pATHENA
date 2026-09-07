from __future__ import annotations

import uuid

import pytest

from athena.memory.feedback import rejected_personal_memory_feedback
from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemoryScopeKind,
    MemorySensitivity,
    ModelInferredMemoryProposal,
    PersonalMemoryDraft,
)


def _proposal(*, scope_entity_id: uuid.UUID | None = None) -> ModelInferredMemoryProposal:
    scope_kind = MemoryScopeKind.PROJECT if scope_entity_id is not None else MemoryScopeKind.GLOBAL
    return ModelInferredMemoryProposal(
        draft=PersonalMemoryDraft(
            memory_kind=MemoryKind.RESPONSE_STYLE,
            content="Use concise answers.",
            scope_kind=scope_kind,
            scope_entity_id=scope_entity_id,
            learning_mode=MemoryLearningMode.MODEL_INFERRED,
            sensitivity=MemorySensitivity.NORMAL,
            confidence=0.9,
        ),
        model_signature_id=uuid.uuid4(),
        processing_run_id=uuid.uuid4(),
    )


def test_rejected_feedback_preserves_only_real_non_content_proposal_metadata() -> None:
    proposal = _proposal()

    feedback = rejected_personal_memory_feedback(proposal)

    assert feedback.model_signature_id == proposal.model_signature_id
    assert feedback.processing_run_id == proposal.processing_run_id
    assert feedback.memory_kind is proposal.draft.memory_kind
    assert feedback.scope_kind is proposal.draft.scope_kind
    assert feedback.scope_entity_id is None
    assert not hasattr(feedback, "content")
    assert not hasattr(feedback, "draft")
    assert not hasattr(feedback, "confidence")


def test_rejected_feedback_preserves_real_scope_without_synthetic_identity() -> None:
    scope_entity_id = uuid.uuid4()
    proposal = _proposal(scope_entity_id=scope_entity_id)

    feedback = rejected_personal_memory_feedback(proposal)

    assert feedback.scope_kind is MemoryScopeKind.PROJECT
    assert feedback.scope_entity_id == scope_entity_id


def test_rejected_feedback_rejects_untyped_runtime_values() -> None:
    with pytest.raises(TypeError, match="ModelInferredMemoryProposal"):
        rejected_personal_memory_feedback(object())  # type: ignore[arg-type]
