from __future__ import annotations

import uuid
from unittest.mock import Mock

from athena.chat.service import ChatService
from athena.memory.models import (
    MemoryKind,
    MemoryLearningMode,
    MemoryScopeKind,
    MemorySensitivity,
    PersonalMemoryDraft,
    PersonalMemoryRevision,
)
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService


def test_explicit_save_creates_one_user_revision_without_model_signature() -> None:
    repository = Mock(spec=PersonalMemoryRepository)
    chat = Mock(spec=ChatService)
    actor_id = uuid.uuid4()
    revision = PersonalMemoryRevision(
        memory_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        revision_no=1,
        created_at_us=1,
        created_by_actor_id=actor_id,
        provenance_id=uuid.uuid4(),
        payload=PersonalMemoryDraft(
            memory_kind=MemoryKind.DETAIL_PREFERENCE,
            content="I prefer concise answers.",
            scope_kind=MemoryScopeKind.GLOBAL,
            learning_mode=MemoryLearningMode.EXPLICIT_USER,
            sensitivity=MemorySensitivity.NORMAL,
            last_confirmed_at_us=1,
        ),
    )
    repository.create.return_value = revision
    chat.ensure_local_user.return_value = actor_id
    chat.load_chat.return_value = object()
    chat.add_user_message.return_value = Mock()

    service = PersonalMemoryService(repository=repository, chat=chat)
    result = service.remember_explicit_chat_command(
        chat_id=uuid.uuid4(),
        content="Please remember that I prefer concise answers.",
    )

    assert result is not None
    assert result.memory_revision is revision
    assert result.memory_revision.revision_no == 1
    assert result.memory_revision.created_by_actor_id == actor_id
    assert result.memory_revision.payload.learning_mode is MemoryLearningMode.EXPLICIT_USER

    repository.create.assert_called_once()
    create_kwargs = repository.create.call_args.kwargs
    assert create_kwargs["actor_id"] == actor_id
    assert create_kwargs["draft"].content == "I prefer concise answers."
    assert create_kwargs["draft"].learning_mode is MemoryLearningMode.EXPLICIT_USER
    assert "model_signature_id" not in create_kwargs
    assert "processing_run_id" not in create_kwargs
