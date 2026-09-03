"""Adapters from established retrieval results into the canonical Search API DTO."""

from __future__ import annotations

from athena.api.search_contracts import (
    SearchProtectionResponse,
    SearchResultResponse,
)
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.protection import unprotected_search_protection_ref


def hybrid_search_result_response(result: HybridSearchResult) -> SearchResultResponse:
    """Serialize one normal Hybrid retrieval result without inventing provenance.

    Normal Hybrid retrieval is backed by the unprotected FTS/semantic projection.
    It therefore carries an explicit unprotected classification and no source
    anchor. Archive/protected result types require their own adapters because
    their source/protection provenance is materially different.
    """

    if not isinstance(result, HybridSearchResult):
        raise TypeError("Search adapter requires a HybridSearchResult.")
    if result.rank is None:
        raise ValueError("Hybrid Search result must have a final rank before serialization.")

    protection = unprotected_search_protection_ref()
    return SearchResultResponse(
        result_ref=f"{result.entity_type.value}:{result.entity_id}",
        title=result.title,
        preview=result.text,
        entity_type=result.entity_type.value,
        revision_id=str(result.revision_id),
        rank=result.rank,
        retrieval_methods=result.retrieval_methods,
        source_anchor=None,
        protection=SearchProtectionResponse(
            state=protection.state.value,
            protection_scope_id=None,
        ),
    )
