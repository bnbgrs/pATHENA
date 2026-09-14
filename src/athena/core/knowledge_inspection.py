"""Composition helpers for canonical Claim inspection.

Keep construction of the Claim inspection chain in one place so callers cannot
accidentally introduce a second repository, review queue, actor identity, or DTO
path while wiring the application.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from athena.api.knowledge_inspection import KnowledgeInspectionApiService
from athena.knowledge.claim_repository import ClaimRepository
from athena.knowledge.inspection_service import KnowledgeInspectionService
from athena.knowledge.review_service import ReviewService


def build_knowledge_inspection_api(
    *,
    claims: ClaimRepository,
    reviews: ReviewService,
    actor_id_provider: Callable[[], uuid.UUID],
) -> KnowledgeInspectionApiService:
    """Build the canonical Claim inspection chain from existing app services."""

    inspection = KnowledgeInspectionService(
        claims=claims,
        reviews=reviews,
    )
    return KnowledgeInspectionApiService(
        inspection=inspection,
        actor_id_provider=actor_id_provider,
    )
