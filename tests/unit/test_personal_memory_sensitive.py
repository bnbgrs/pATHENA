from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest

from athena.chat.service import ChatService
from athena.memory.models import MemoryKind, MemorySensitivity
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import (
    PersonalMemoryInferenceApprovalRequiredError,
    PersonalMemoryService,
)


@pytest.mark.parametrize(
    "sensitivity",
    [MemorySensitivity.SENSITIVE, MemorySensitivity.PROTECTED],
)
def test_sensitive_model_inference_fails_closed_before_canonical_write(
    sensitivity: MemorySensitivity,
) -> None:
    repository = Mock(spec=PersonalMemoryRepository)
    chat = Mock(spec=ChatService)
    service = PersonalMemoryService(repository=repository, chat=chat)

    with pytest.raises(
        PersonalMemoryInferenceApprovalRequiredError,
        match="requires explicit user approval",
    ):
        service.propose_model_inferred(
            content="Automatically recognized sensitive information.",
            memory_kind=MemoryKind.DETAIL_PREFERENCE,
            model_signature_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            confidence=0.97,
            sensitivity=sensitivity,
        )

    repository.create.assert_not_called()
    chat.ensure_local_user.assert_not_called()
