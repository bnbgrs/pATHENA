"""Direct user Knowledge creation without fabricated external sources."""

from __future__ import annotations

import uuid

from athena.knowledge.models import KnowledgeUnitDraft, KnowledgeUnitRevision
from athena.knowledge.repository import KnowledgeRepository


def create_orphan_user_knowledge(
    *,
    repository: KnowledgeRepository,
    actor_id: uuid.UUID,
    draft: KnowledgeUnitDraft,
) -> KnowledgeUnitRevision:
    """Create direct user Knowledge with provenance but no external Source input.

    Beta §65 permits canonical Knowledge that has no Source, such as a direct
    user decision. The repository still creates the normal provenance record;
    this use case deliberately supplies no source entity or source revision so
    the absence of external evidence remains explicit instead of being filled
    with synthetic provenance.
    """
    if not isinstance(repository, KnowledgeRepository):
        raise TypeError("repository must be a KnowledgeRepository.")
    if not isinstance(actor_id, uuid.UUID):
        raise TypeError("actor_id must be a UUID.")
    if not isinstance(draft, KnowledgeUnitDraft):
        raise TypeError("draft must be a KnowledgeUnitDraft.")

    return repository.create_knowledge_unit(
        actor_id=actor_id,
        draft=draft,
        reason="direct user knowledge without external source",
    )
