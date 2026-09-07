from __future__ import annotations

import uuid

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.memory.models import MemoryKind, MemoryLearningMode
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService
from athena.storage.database import SQLiteDatabase


def _service(tmp_path) -> tuple[PersonalMemoryService, SQLiteDatabase]:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    return PersonalMemoryService(PersonalMemoryRepository(database), chat), database


def test_explicit_review_accepts_inferred_memory_with_durable_model_provenance(tmp_path) -> None:
    memory, database = _service(tmp_path)
    model_signature_id = uuid.uuid4()
    processing_run_id = uuid.uuid4()
    proposal = memory.propose_model_inferred(
        content="Prefer terse code-review summaries.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
        model_signature_id=model_signature_id,
        processing_run_id=processing_run_id,
        confidence=0.88,
    )

    accepted = memory.accept_model_inferred(proposal)

    assert accepted.payload.learning_mode is MemoryLearningMode.MODEL_INFERRED
    assert accepted.payload.last_confirmed_at_us is not None
    assert memory.load(accepted.memory_id).revision == accepted
    row = database.connection.execute(
        """
        SELECT model_signature_id, processing_run_id
        FROM provenance_records
        WHERE provenance_id = ?
        """,
        (uuid_to_blob(accepted.provenance_id),),
    ).fetchone()
    assert row is not None
    assert uuid_from_blob(bytes(row["model_signature_id"])) == model_signature_id
    assert uuid_from_blob(bytes(row["processing_run_id"])) == processing_run_id


def test_review_acceptance_creates_new_memory_without_overwriting_explicit_user_memory(tmp_path) -> None:
    memory, _ = _service(tmp_path)
    explicit = memory.remember(
        content="Always keep explicit preference.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
    )
    proposal = memory.propose_model_inferred(
        content="Prefer inferred concise summaries.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
        model_signature_id=uuid.uuid4(),
        processing_run_id=uuid.uuid4(),
        confidence=0.82,
    )

    accepted = memory.accept_model_inferred(proposal)

    assert accepted.memory_id != explicit.memory_id
    assert memory.load(explicit.memory_id).revision == explicit
    assert memory.load(explicit.memory_id).revision.payload.learning_mode is MemoryLearningMode.EXPLICIT_USER
    assert len(memory.list()) == 2
