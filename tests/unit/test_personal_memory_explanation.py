from __future__ import annotations

import uuid

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.memory.explanation import explain_personal_memory
from athena.memory.models import MemoryKind, MemoryLearningMode
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService
from athena.storage.database import SQLiteDatabase


def _services(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    repository = PersonalMemoryRepository(database)
    memory = PersonalMemoryService(repository, chat)
    return database, repository, memory


def test_explanation_for_explicit_memory_uses_only_canonical_revision_metadata(tmp_path) -> None:
    database, repository, memory = _services(tmp_path)
    created = memory.remember(
        content="Prefer concise answers.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
    )

    explanation = explain_personal_memory(repository.load_current(created.memory_id))

    assert explanation.memory_id == created.memory_id
    assert explanation.revision_id == created.revision_id
    assert explanation.origin is MemoryLearningMode.EXPLICIT_USER
    assert explanation.last_changed_at_us == created.created_at_us
    assert explanation.last_confirmed_at_us == created.payload.last_confirmed_at_us
    assert not hasattr(explanation, "content")
    database.stop()


def test_explanation_for_accepted_model_inference_reports_model_inferred_origin(tmp_path) -> None:
    database, repository, memory = _services(tmp_path)
    proposal = memory.propose_model_inferred(
        content="Prefer concise answers.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
        model_signature_id=uuid.uuid4(),
        processing_run_id=uuid.uuid4(),
        confidence=0.9,
    )
    accepted = memory.accept_model_inferred(proposal)

    explanation = explain_personal_memory(repository.load_current(accepted.memory_id))

    assert explanation.memory_id == accepted.memory_id
    assert explanation.revision_id == accepted.revision_id
    assert explanation.origin is MemoryLearningMode.MODEL_INFERRED
    assert explanation.last_changed_at_us == accepted.created_at_us
    assert explanation.last_confirmed_at_us == accepted.payload.last_confirmed_at_us
    assert not hasattr(explanation, "content")
    database.stop()
