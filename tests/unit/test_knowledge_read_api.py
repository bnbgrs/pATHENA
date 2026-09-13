from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.api.knowledge_explanation import KnowledgeProvenanceExplanationResponse
from athena.api.knowledge_history import KnowledgeHistoryResponse
from athena.api.knowledge_read import KnowledgeReadApiService

KNOWLEDGE_ID = "11111111-1111-4111-8111-111111111111"


@dataclass
class _ExplanationStub:
    response: KnowledgeProvenanceExplanationResponse
    seen: list[str]
    error: Exception | None = None

    def why_known(self, knowledge_id: str) -> KnowledgeProvenanceExplanationResponse:
        self.seen.append(knowledge_id)
        if self.error is not None:
            raise self.error
        return self.response


@dataclass
class _HistoryStub:
    response: KnowledgeHistoryResponse
    seen: list[str]
    error: Exception | None = None

    def revision_history(self, knowledge_id: str) -> KnowledgeHistoryResponse:
        self.seen.append(knowledge_id)
        if self.error is not None:
            raise self.error
        return self.response


def _service() -> tuple[KnowledgeReadApiService, _ExplanationStub, _HistoryStub]:
    explanation = _ExplanationStub(
        response=KnowledgeProvenanceExplanationResponse(
            knowledge_id=KNOWLEDGE_ID,
            revision_id="22222222-2222-4222-8222-222222222222",
            revision_no=2,
            created_at_us=20,
            actor_id="33333333-3333-4333-8333-333333333333",
            inputs=(),
            text="Recorded provenance explanation.",
        ),
        seen=[],
    )
    history = _HistoryStub(
        response=KnowledgeHistoryResponse(
            knowledge_id=KNOWLEDGE_ID,
            entries=(),
        ),
        seen=[],
    )
    service = KnowledgeReadApiService(
        explanation=explanation,
        history=history,
    )
    return service, explanation, history


def test_why_known_delegates_exact_identity_and_returns_existing_projection() -> None:
    service, explanation, history = _service()

    response = service.why_known(KNOWLEDGE_ID)

    assert response is explanation.response
    assert explanation.seen == [KNOWLEDGE_ID]
    assert history.seen == []


def test_revision_history_delegates_exact_identity_and_returns_existing_projection() -> None:
    service, explanation, history = _service()

    response = service.revision_history(KNOWLEDGE_ID)

    assert response is history.response
    assert history.seen == [KNOWLEDGE_ID]
    assert explanation.seen == []


def test_explanation_errors_are_not_downgraded_or_reinterpreted() -> None:
    service, explanation, _history = _service()
    explanation.error = ValueError("invalid knowledge identity")

    with pytest.raises(ValueError, match="invalid knowledge identity"):
        service.why_known("not-a-uuid")


def test_history_errors_are_not_downgraded_or_reinterpreted() -> None:
    service, _explanation, history = _service()
    history.error = LookupError("knowledge history unavailable")

    with pytest.raises(LookupError, match="knowledge history unavailable"):
        service.revision_history(KNOWLEDGE_ID)
