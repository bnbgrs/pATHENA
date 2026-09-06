from __future__ import annotations

import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.memory.export import (
    PersonalMemoryExportProtectionError,
    export_personal_memory,
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


def test_personal_memory_export_uses_only_canonical_current_sqlite_state(tmp_path) -> None:
    database, repository, memory = _services(tmp_path)
    first = memory.remember(
        content="Prefer concise answers.",
        memory_kind=MemoryKind.DETAIL_PREFERENCE,
    )
    second = memory.remember(
        content="Use the local provider when available.",
        memory_kind=MemoryKind.MODEL_PREFERENCE,
        sensitivity=MemorySensitivity.SENSITIVE,
    )
    revised = memory.revise(
        memory_id=first.memory_id,
        content="Prefer concise technical answers.",
    )

    snapshots = repository.list_current(limit=50, include_inactive=True)
    exported = export_personal_memory(snapshots)
    by_id = {entry.memory_id: entry for entry in exported}

    assert set(by_id) == {first.memory_id, second.memory_id}
    assert by_id[first.memory_id].revision_id == revised.revision_id
    assert by_id[first.memory_id].revision_no == 2
    assert by_id[first.memory_id].content == "Prefer concise technical answers."
    assert by_id[second.memory_id].revision_id == second.revision_id
    assert by_id[second.memory_id].sensitivity is MemorySensitivity.SENSITIVE
    database.stop()


def test_personal_memory_export_fails_closed_for_protected_plaintext_snapshot() -> None:
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

    with pytest.raises(PersonalMemoryExportProtectionError, match="Protected Content export path"):
        export_personal_memory((snapshot,))


def test_personal_memory_export_rejects_duplicate_current_identity() -> None:
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
            content="one current entry",
        ),
    )
    snapshot = PersonalMemorySnapshot(
        memory_id=memory_id,
        lifecycle_state="active",
        revision=revision,
    )

    with pytest.raises(ValueError, match="one current snapshot per memory_id"):
        export_personal_memory((snapshot, snapshot))
