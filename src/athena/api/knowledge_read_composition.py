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


def build_knowledge_read_api(*, knowledge: KnowledgeReadSource) -> KnowledgeReadApiService:
    """Compose existing truthful read projections over one canonical Knowledge source."""

    explanation = KnowledgeExplanationApiService(knowledge=knowledge)
    history = KnowledgeHistoryApiService(knowledge=knowledge)
    return KnowledgeReadApiService(
        explanation=explanation,
        history=history,
    )
