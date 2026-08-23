from __future__ import annotations

import math
import struct
import uuid

import pytest

from athena.retrieval.search import SearchEntityType
from athena.retrieval.semantic import (
    EmbeddingIndexStatus,
    SemanticSearchError,
    SemanticSearchResult,
    _decode_reference,
    _normalize_vector,
    _pack_vector,
    _storage_model_id,
    _unpack_vector,
)


def test_embedding_status_rejects_invalid_persisted_shape() -> None:
    with pytest.raises(SemanticSearchError):
        EmbeddingIndexStatus(
            model_id="embed",
            indexed_commit_seq=-1,
            current_commit_seq=0,
            dimensions=0,
            document_count=-1,
            rebuilt_at_us=-1,
            hnsw_ready=True,
        )


@pytest.mark.parametrize("value", [True, False, 1.5, "1", None])
def test_embedding_status_rejects_non_integer_counters(value: object) -> None:
    with pytest.raises(SemanticSearchError):
        EmbeddingIndexStatus(
            model_id="embed",
            indexed_commit_seq=value,  # type: ignore[arg-type]
            current_commit_seq=0,
            dimensions=1,
            document_count=0,
            rebuilt_at_us=0,
            hnsw_ready=True,
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), True])
def test_semantic_result_rejects_invalid_similarity(value: object) -> None:
    with pytest.raises(SemanticSearchError):
        SemanticSearchResult(
            entity_id=uuid.uuid4(),
            revision_id=uuid.uuid4(),
            entity_type=SearchEntityType.KNOWLEDGE,
            title=None,
            text="evidence",
            similarity=value,  # type: ignore[arg-type]
            contradiction_count=0,
        )


def test_semantic_result_rejects_similarity_outside_cosine_range() -> None:
    with pytest.raises(SemanticSearchError, match="between -1 and 1"):
        SemanticSearchResult(
            entity_id=uuid.uuid4(),
            revision_id=uuid.uuid4(),
            entity_type=SearchEntityType.KNOWLEDGE,
            title=None,
            text="evidence",
            similarity=1.01,
            contradiction_count=0,
        )


@pytest.mark.parametrize(
    "vector",
    [
        (float("nan"), 1.0),
        (float("inf"), 1.0),
        (float("-inf"), 1.0),
        (True, 1.0),
        (),
    ],
)
def test_normalize_vector_rejects_invalid_components(vector: tuple[object, ...]) -> None:
    with pytest.raises(SemanticSearchError):
        _normalize_vector(vector)  # type: ignore[arg-type]


def test_normalize_vector_handles_large_finite_components_without_square_overflow() -> None:
    normalized = _normalize_vector((1e308, 1e308))

    assert all(math.isfinite(component) for component in normalized)
    assert math.isclose(math.hypot(*normalized), 1.0)


def test_pack_vector_rejects_float32_overflow() -> None:
    with pytest.raises(SemanticSearchError, match="float32"):
        _pack_vector((1e308,))


def test_unpack_vector_rejects_non_finite_persisted_float32() -> None:
    blob = struct.pack("<f", float("nan"))

    with pytest.raises(SemanticSearchError, match="non-finite"):
        _unpack_vector(blob, 1)


@pytest.mark.parametrize("dimensions", [True, False, 0, -1, 1.5, "1"])
def test_unpack_vector_rejects_invalid_dimension_contract(dimensions: object) -> None:
    with pytest.raises(SemanticSearchError):
        _unpack_vector(b"\x00\x00\x00\x00", dimensions)  # type: ignore[arg-type]


def test_decode_reference_rejects_non_bytes() -> None:
    with pytest.raises(SemanticSearchError, match="must be bytes"):
        _decode_reference(bytearray(33))  # type: ignore[arg-type]


def test_storage_model_id_rejects_non_text_model_id() -> None:
    with pytest.raises(SemanticSearchError, match="must be text"):
        _storage_model_id(123)  # type: ignore[arg-type]
