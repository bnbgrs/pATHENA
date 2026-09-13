"""Unified transport-neutral read surface for truthful Knowledge audit data."""

from __future__ import annotations

from typing import Protocol

from athena.api.knowledge_explanation import KnowledgeProvenanceExplanationResponse
from athena.api.knowledge_history import KnowledgeHistoryResponse


class KnowledgeExplanationReader(Protocol):
    """Existing provenance-explanation boundary consumed by the composition."""

    def why_known(self, knowledge_id: str) -> KnowledgeProvenanceExplanationResponse: ...


class KnowledgeHistoryReader(Protocol):
    """Existing revision-history boundary consumed by the composition."""

    def revision_history(self, knowledge_id: str) -> KnowledgeHistoryResponse: ...


class KnowledgeReadApiService:
    """Compose existing Knowledge explanation and history services without bypassing them."""

    def __init__(
        self,
        *,
        explanation: KnowledgeExplanationReader,
        history: KnowledgeHistoryReader,
    ) -> None:
        self._explanation = explanation
        self._history = history

    def why_known(self, knowledge_id: str) -> KnowledgeProvenanceExplanationResponse:
        """Return the existing truthful provenance explanation projection."""
        return self._explanation.why_known(knowledge_id)

    def revision_history(self, knowledge_id: str) -> KnowledgeHistoryResponse:
        """Return the existing immutable revision-history projection."""
        return self._history.revision_history(knowledge_id)
