from __future__ import annotations

import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.memory.context import (
    PERSONAL_MEMORY_CONTEXT_LABEL,
    PersonalMemoryContextProtectionError,
    personal_memory_context,
)
from athena.memory.models import (
    MemoryKind,
    MemorySensitivity,
    PersonalMemoryDraft,
    PersonalMemoryRevision,
    PersonalMemorySnapshot,
)
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


def test_personal_memory_context_labels_real_active_sqlite_memory_as_user_preference(tmp_path) -> None:
    database, repository, memory = _services(tmp_path)
    active = memory.remember(
        content="Prefer concise technical answers.",
        memory_kind=MemoryKind.RESPONSE_STYLE,
    )
    inactive = memory.remember(
        content="Use long prose.",
        memory_kind=MemoryKind.RESPONSE_STYLE,
    )
    memory.disable(inactive.memory_id)

    snapshots = repository.list_current(limit=50, include_inactive=True)
    entries = personal_memory_context(snapshots)

    assert len(entries) == 1
    entry = entries[0]
    assert entry.label == PERSONAL_MEMORY_CONTEXT_LABEL == "USER PREFERENCE"
    assert entry.memory_id == active.memory_id
    assert entry.revision_id == active.revision_id
    assert entry.content == "Prefer concise technical answers."
    assert "FACT ABOUT THE WORLD" not in entry.label
    database.stop()


def test_personal_memory_context_fails_closed_for_protected_plaintext_snapshot() -> None:
    memory_id = uuid.uuid4()
    revision = PersonalMemoryRevision(
        memory_id=memory_id,
        revision_id=uuid.uuid4(),
        revision_no=1,
        created_at_us=1,
        created_by_actor_id=uuid.uuid4(),
        provenance_id=uuid.uuid4(),
        payload=PersonalMemoryDraft(
            memory_kind=MemoryKind.OTHER,
            content="must remain protected",
            sensitivity=MemorySensitivity.PROTECTED,
        ),
    )
    snapshot = PersonalMemorySnapshot(
        memory_id=memory_id,
        lifecycle_state="active",
        revision=revision,
    )

    with pytest.raises(PersonalMemoryContextProtectionError, match="Protected Content context path"):
        personal_memory_context((snapshot,))


def test_personal_memory_context_rejects_duplicate_current_identity() -> None:
    memory_id = uuid.uuid4()
    revision = PersonalMemoryRevision(
        memory_id=memory_id,
        revision_id=uuid.uuid4(),
        revision_no=1,
        created_at_us=1,
        created_by_actor_id=uuid.uuid4(),
        provenance_id=uuid.uuid4(),
        payload=PersonalMemoryDraft(
            memory_kind=MemoryKind.OTHER,
            content="one current preference",
        ),
    )
    snapshot = PersonalMemorySnapshot(
        memory_id=memory_id,
        lifecycle_state="active",
        revision=revision,
    )

    with pytest.raises(ValueError, match="one current snapshot per memory_id"):
        personal_memory_context((snapshot, snapshot))
