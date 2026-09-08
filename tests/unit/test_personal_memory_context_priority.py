from __future__ import annotations

import json
import uuid

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.memory.models import MemoryKind, MemoryScopeKind
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService
from athena.retrieval.context import ContextBuilderService
from athena.storage.database import SQLiteDatabase


def test_exact_scoped_memory_priority_reaches_model_facing_context(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    memory = PersonalMemoryService(PersonalMemoryRepository(database), chat)
    project_id = uuid.uuid4()

    global_core = memory.remember(
        content="Prefer German.",
        memory_kind=MemoryKind.LANGUAGE_PREFERENCE,
    )
    global_fallback = memory.remember(
        content="Prefer a stable default export path.",
        memory_kind=MemoryKind.WORKFLOW_PREFERENCE,
    )
    exact_scoped = memory.remember(
        content="For this project, answer with implementation details.",
        memory_kind=MemoryKind.WORKFLOW_PREFERENCE,
        scope_kind=MemoryScopeKind.PROJECT,
        scope_entity_id=project_id,
    )

    candidates = memory.context_candidates(
        scope_kind=MemoryScopeKind.PROJECT,
        scope_entity_id=project_id,
    )
    bundle = ContextBuilderService().build_from_ranked(
        query="This time answer briefly.",
        results=(),
        personal_memory=candidates,
        max_estimated_tokens=900,
        max_memory_items=8,
    )

    payload = json.loads(bundle.rendered_text)
    preferences = payload["user_preferences"]
    assert [item["memory_id"] for item in preferences] == [
        str(exact_scoped.memory_id),
        str(global_core.memory_id),
        str(global_fallback.memory_id),
    ]
    assert all(item["label"] == "USER PREFERENCE" for item in preferences)
    assert preferences[0]["scope_kind"] == MemoryScopeKind.PROJECT.value
    assert preferences[0]["scope_entity_id"] == str(project_id)
    assert payload["query"] == "This time answer briefly."
    assert "Current user message overrides USER PREFERENCE" in payload["policy"]

    database.stop()
