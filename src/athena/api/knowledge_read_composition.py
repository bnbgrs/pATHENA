"""Canonical composition for truthful Knowledge provenance and revision reads."""

from __future__ import annotations

from typing import Protocol

from athena.api.knowledge_explanation import (
    KnowledgeExplanationApiService,
    KnowledgeProvenanceReader,
)
from athena.api.knowledge_history import (
    KnowledgeHistoryApiService,
    KnowledgeHistoryReader,
)
from athena.api.knowledge_read import KnowledgeReadApiService


class KnowledgeReadSource(KnowledgeProvenanceReader, KnowledgeHistoryReader, Protocol):
    """Single canonical Knowledge reader required by both audit projections."""


class KnowledgeReadFacade(Protocol):
    """Facade boundary required to expose the canonical Knowledge reader."""

    def attach_knowledge_read(self, service: KnowledgeReadApiService) -> None:
        """Attach exactly one Knowledge read API service."""


def build_knowledge_read_api(*, knowledge: KnowledgeReadSource) -> KnowledgeReadApiService:
    """Compose existing truthful read projections over one canonical Knowledge source."""

    explanation = KnowledgeExplanationApiService(knowledge=knowledge)
    history = KnowledgeHistoryApiService(knowledge=knowledge)
    return KnowledgeReadApiService(
        explanation=explanation,
        history=history,
    )


def attach_knowledge_read_api(
    *,
    facade: KnowledgeReadFacade,
    knowledge: KnowledgeReadSource,
) -> KnowledgeReadApiService:
    """Build, attach and return one canonical Knowledge read service instance."""

    service = build_knowledge_read_api(knowledge=knowledge)
    facade.attach_knowledge_read(service)
    return service
