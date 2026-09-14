"""Composition helpers for canonical Claim inspection.

Keep construction of the Claim inspection chain in one place so callers cannot
accidentally introduce a second repository, review queue, actor identity, or DTO
path while wiring the application.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from athena.api.knowledge_inspection import KnowledgeInspectionApiService
from athena.api.service import CoreApiFacade
from athena.knowledge.inspection_service import ClaimReader, KnowledgeInspectionService
from athena.knowledge.review_service import ReviewService


def build_knowledge_inspection_api(
    *,
    claims: ClaimReader,
    reviews: ReviewService,
    actor_id_provider: Callable[[], uuid.UUID],
) -> KnowledgeInspectionApiService:
    """Build Claim inspection from the application's existing canonical services."""

    inspection = KnowledgeInspectionService(
        claims=claims,
        reviews=reviews,
    )
    return KnowledgeInspectionApiService(
        inspection=inspection,
        actor_id_provider=actor_id_provider,
    )


def attach_knowledge_inspection_api(
    *,
    facade: CoreApiFacade,
    claims: ClaimReader,
    reviews: ReviewService,
    actor_id_provider: Callable[[], uuid.UUID],
) -> KnowledgeInspectionApiService:
    """Build and attach one canonical Claim-inspection API instance."""

    inspection_api = build_knowledge_inspection_api(
        claims=claims,
        reviews=reviews,
        actor_id_provider=actor_id_provider,
    )
    facade.attach_knowledge_inspection(inspection_api)
    return inspection_api
