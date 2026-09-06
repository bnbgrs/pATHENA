from __future__ import annotations

import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemoryScopeKind,
    MemorySensitivity,
    PersonalMemoryDraft,
    PersonalMemoryRevision,
    PersonalMemorySnapshot,
)
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService
from athena.memory.view import PersonalMemoryViewProtectionError, personal_memory_view
from athena.storage.database import SQLiteDatabase


def _services(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    repository = PersonalMemoryRepository(database)
    memory = PersonalMemoryService(repository, chat)
    return database, repository, memory


def test_memory_view_projects_current_state_and_real_revision_history(tmp_path) -> None:
    database, repository, memory = _services(tmp_path)
    project_id = uuid.uuid4()
    created = memory.remember(
        content="Use terse technical answers.",
        memory_kind=MemoryKind.RESPONSE_STYLE,
        scope_kind=MemoryScopeKind.PROJECT,
        scope_entity_id=project_id,
        sensitivity=MemorySensitivity.SENSITIVE,
    )
    revised = memory.revise(
        memory_id=created.memory_id,
        content="Use concise technical answers.",
    )

    snapshot = repository.load_current(created.memory_id)
    history = repository.list_revisions(created.memory_id)
    view = personal_memory_view(snapshot, history)

    assert view.memory_id == created.memory_id
    assert view.current_revision_id == revised.revision_id
    assert view.lifecycle_state == "active"
    assert view.content == "Use concise technical answers."
    assert view.memory_kind is MemoryKind.RESPONSE_STYLE
    assert view.scope_kind is MemoryScopeKind.PROJECT
    assert view.scope_entity_id == project_id
    assert view.origin is MemoryLearningMode.EXPLICIT_USER
    assert view.sensitivity is MemorySensitivity.SENSITIVE
    assert view.confidence is None
    assert view.last_confirmed_at_us == revised.payload.last_confirmed_at_us
    assert [item.revision_id for item in view.revisions] == [
        created.revision_id,
        revised.revision_id,
    ]
    assert [item.revision_no for item in view.revisions] == [1, 2]
    assert all(not hasattr(item, "content") for item in view.revisions)
    database.stop()


def test_memory_view_fails_closed_for_protected_plaintext_snapshot() -> None:
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
            content="must not escape",
            sensitivity=MemorySensitivity.PROTECTED,
        ),
    )
    snapshot = PersonalMemorySnapshot(
        memory_id=memory_id,
        lifecycle_state="active",
        revision=revision,
    )

    with pytest.raises(PersonalMemoryViewProtectionError, match="Protected Content view path"):
        personal_memory_view(snapshot, (revision,))
