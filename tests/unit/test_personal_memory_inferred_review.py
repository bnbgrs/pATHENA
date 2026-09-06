from __future__ import annotations

import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemorySensitivity,
)
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import (
    PersonalMemoryInferenceApprovalRequiredError,
    PersonalMemoryService,
)
from athena.storage.database import SQLiteDatabase


def _service(tmp_path) -> PersonalMemoryService:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    return PersonalMemoryService(PersonalMemoryRepository(database), chat)


def test_model_inferred_default_suggest_is_noncanonical_and_keeps_provenance(tmp_path) -> None:
    memory = _service(tmp_path)
    model_signature_id = uuid.uuid4()
    processing_run_id = uuid.uuid4()

    proposal = memory.propose_model_inferred(
        content="Prefer concise implementation notes.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
        model_signature_id=model_signature_id,
        processing_run_id=processing_run_id,
        confidence=0.91,
    )

    assert proposal.review_required is True
    assert proposal.model_signature_id == model_signature_id
    assert proposal.processing_run_id == processing_run_id
    assert proposal.draft.learning_mode is MemoryLearningMode.MODEL_INFERRED
    assert proposal.draft.confidence == 0.91
    assert memory.list() == ()


def test_sensitive_model_inference_fails_closed_without_canonical_write(tmp_path) -> None:
    memory = _service(tmp_path)

    with pytest.raises(PersonalMemoryInferenceApprovalRequiredError):
        memory.propose_model_inferred(
            content="Sensitive inferred preference.",
            memory_kind=MemoryKind.OTHER,
            model_signature_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            confidence=0.99,
            sensitivity=MemorySensitivity.SENSITIVE,
        )

    assert memory.list() == ()
