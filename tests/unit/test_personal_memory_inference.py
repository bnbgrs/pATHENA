from __future__ import annotations

import uuid
from unittest.mock import Mock

from athena.chat.service import ChatService
from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemorySensitivity,
)
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService


def test_model_inference_preserves_real_provenance_and_requires_review_before_write() -> None:
    repository = Mock(spec=PersonalMemoryRepository)
    chat = Mock(spec=ChatService)
    service = PersonalMemoryService(repository=repository, chat=chat)
    model_signature_id = uuid.uuid4()
    processing_run_id = uuid.uuid4()

    proposal = service.propose_model_inferred(
        content="Use concise answers.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
        model_signature_id=model_signature_id,
        processing_run_id=processing_run_id,
        confidence=0.91,
    )

    assert proposal.model_signature_id == model_signature_id
    assert proposal.processing_run_id == processing_run_id
    assert proposal.review_required is True
    assert proposal.draft.learning_mode is MemoryLearningMode.MODEL_INFERRED
    assert proposal.draft.sensitivity is MemorySensitivity.NORMAL
    assert proposal.draft.confidence == 0.91
    assert proposal.draft.last_confirmed_at_us is None
    repository.create.assert_not_called()
    chat.ensure_local_user.assert_not_called()
