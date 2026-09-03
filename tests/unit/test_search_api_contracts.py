from __future__ import annotations

import uuid

import pytest

from athena.api.search_contracts import (
    SearchProtectionResponse,
    SearchResultResponse,
    SearchSourceAnchorResponse,
)


def test_search_result_response_serializes_required_beta_fields() -> None:
    revision_id = uuid.uuid4()
    representation_id = uuid.uuid4()
    scope_id = uuid.uuid4()

    response = SearchResultResponse(
        result_ref="source-chunk:7",
        title="Reference source",
        preview="Relevant excerpt",
        entity_type="source_chunk",
        revision_id=str(revision_id),
        rank=1,
        retrieval_methods=("lexical", "semantic"),
        source_anchor=SearchSourceAnchorResponse(
            representation_id=str(representation_id),
            start_offset=10,
            end_offset=25,
            quoted_sha256="ab" * 32,
        ),
        protection=SearchProtectionResponse(
            state="protected",
            protection_scope_id=str(scope_id),
        ),
    )

    assert response.to_dict() == {
        "result_ref": "source-chunk:7",
        "title": "Reference source",
        "preview": "Relevant excerpt",
        "entity_type": "source_chunk",
        "revision_id": str(revision_id),
        "rank": 1,
        "retrieval_methods": ["lexical", "semantic"],
        "source_anchor": {
            "representation_id": str(representation_id),
            "start_offset": 10,
            "end_offset": 25,
            "quoted_sha256": "ab" * 32,
        },
        "protection": {
            "state": "protected",
            "protection_scope_id": str(scope_id),
        },
    }


def test_unprotected_response_cannot_leak_scope_metadata() -> None:
    with pytest.raises(ValueError, match="must not expose"):
        SearchProtectionResponse(
            state="unprotected",
            protection_scope_id=str(uuid.uuid4()),
        )


def test_protected_response_requires_real_scope_uuid() -> None:
    with pytest.raises(ValueError, match="must retain"):
        SearchProtectionResponse(
            state="protected",
            protection_scope_id=None,
        )

    with pytest.raises(ValueError, match="must be a UUID"):
        SearchProtectionResponse(
            state="protected",
            protection_scope_id="not-a-uuid",
        )


def test_search_response_rejects_invalid_rank_and_duplicate_methods() -> None:
    common = {
        "result_ref": "knowledge:1",
        "title": None,
        "preview": "preview",
        "entity_type": "knowledge",
        "revision_id": str(uuid.uuid4()),
        "source_anchor": None,
        "protection": SearchProtectionResponse(
            state="unprotected",
            protection_scope_id=None,
        ),
    }

    with pytest.raises(TypeError, match="rank must be an integer"):
        SearchResultResponse(
            **common,
            rank=True,
            retrieval_methods=("lexical",),
        )

    with pytest.raises(ValueError, match="must be unique"):
        SearchResultResponse(
            **common,
            rank=1,
            retrieval_methods=("lexical", "lexical"),
        )


def test_search_source_anchor_rejects_invalid_range_and_hash() -> None:
    representation_id = str(uuid.uuid4())

    with pytest.raises(ValueError, match="start_offset < end_offset"):
        SearchSourceAnchorResponse(
            representation_id=representation_id,
            start_offset=5,
            end_offset=5,
            quoted_sha256="ab" * 32,
        )

    with pytest.raises(ValueError, match="SHA-256 hex digest"):
        SearchSourceAnchorResponse(
            representation_id=representation_id,
            start_offset=5,
            end_offset=6,
            quoted_sha256="zz" * 32,
        )
