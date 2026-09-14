from __future__ import annotations

from typing import cast

import pytest

from athena.api.knowledge_read import KnowledgeReadApiService
from athena.api.service import CoreApiFacade
from athena.chat.service import ChatService
from athena.model.ports import ModelDiscoveryProvider
from athena.observability.health import HealthService


class _KnowledgeReadApiStub:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.explanation = object()
        self.history = object()

    def why_known(self, knowledge_id: str) -> object:
        self.calls.append(("why_known", knowledge_id))
        return self.explanation

    def revision_history(self, knowledge_id: str) -> object:
        self.calls.append(("revision_history", knowledge_id))
        return self.history


def _facade() -> CoreApiFacade:
    return CoreApiFacade(
        health=cast(HealthService, object()),
        chat=cast(ChatService, object()),
        model_provider=cast(ModelDiscoveryProvider, object()),
    )


def _knowledge_read_stub() -> tuple[KnowledgeReadApiService, _KnowledgeReadApiStub]:
    stub = _KnowledgeReadApiStub()
    return cast(KnowledgeReadApiService, stub), stub


def test_knowledge_read_capabilities_follow_attachment() -> None:
    facade = _facade()
    knowledge_read, _stub = _knowledge_read_stub()

    assert "knowledge.read.why_known" not in facade.capabilities().features
    assert "knowledge.read.revision_history" not in facade.capabilities().features

    facade.attach_knowledge_read(knowledge_read)

    assert "knowledge.read.why_known" in facade.capabilities().features
    assert "knowledge.read.revision_history" in facade.capabilities().features

    with pytest.raises(RuntimeError, match="already attached"):
        facade.attach_knowledge_read(knowledge_read)


def test_knowledge_read_calls_fail_closed_before_attachment() -> None:
    facade = _facade()
    knowledge_id = "00000000-0000-0000-0000-000000000001"

    with pytest.raises(RuntimeError, match="Knowledge read is unavailable"):
        facade.why_known(knowledge_id)

    with pytest.raises(RuntimeError, match="Knowledge read is unavailable"):
        facade.knowledge_revision_history(knowledge_id)


def test_knowledge_read_facade_delegates_without_rewriting_results() -> None:
    facade = _facade()
    knowledge_read, stub = _knowledge_read_stub()
    facade.attach_knowledge_read(knowledge_read)
    knowledge_id = "00000000-0000-0000-0000-000000000001"

    assert facade.why_known(knowledge_id) is stub.explanation
    assert facade.knowledge_revision_history(knowledge_id) is stub.history
    assert stub.calls == [
        ("why_known", knowledge_id),
        ("revision_history", knowledge_id),
    ]
