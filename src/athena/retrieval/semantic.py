"""Reconstructible local semantic retrieval using infrastructure embeddings."""

from __future__ import annotations

import hashlib
import math
import struct
import uuid
from dataclasses import dataclass
from numbers import Real
from pathlib import Path
from typing import Sequence

from athena.common.ids import uuid_to_blob
from athena.common.time import utc_now_us
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider
from athena.retrieval.hnsw import HnswIndexError, HnswIndexStore
from athena.retrieval.search import (
    SearchEntityType,
    current_search_projection_commit_seq,
)
from athena.storage.database import SQLiteDatabase

_SEMANTIC_TYPE_PRIORITY = {
    SearchEntityType.KNOWLEDGE: 0,
    SearchEntityType.CLAIM: 1,
    SearchEntityType.CHAT_MESSAGE: 2,
}


class SemanticSearchError(RuntimeError):
    """Raised when the semantic derived index cannot be used safely."""


def _canonical_model_id(value: object) -> str:
    if not isinstance(value, str):
        raise SemanticSearchError("Embedding model id must be text.")
    normalized = value.strip()
    if not normalized:
        raise SemanticSearchError("Embedding model id must not be empty.")
    return normalized


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise SemanticSearchError(f"{label} must be a positive integer.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SemanticSearchError(f"{label} must be a non-negative integer.")
    return value


def _persisted_int(value: object, label: str, *, positive: bool = False) -> int:
    if isinstance(value, bool):
        raise SemanticSearchError(f"Persisted {label} is invalid.")
    try:
        normalized = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise SemanticSearchError(f"Persisted {label} is invalid.") from exc
    if positive:
        if normalized < 1:
            raise SemanticSearchError(f"Persisted {label} is invalid.")
    elif normalized < 0:
        raise SemanticSearchError(f"Persisted {label} is invalid.")
    return normalized


def _finite_component(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SemanticSearchError("Embedding vector contains a non-numeric component.")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise SemanticSearchError("Embedding vector contains a non-finite component.") from exc
    if not math.isfinite(normalized):
        raise SemanticSearchError("Embedding vector contains a non-finite component.")
    return normalized


@dataclass(frozen=True, slots=True)
class EmbeddingIndexStatus:
    model_id: str
    indexed_commit_seq: int
    current_commit_seq: int
    dimensions: int
    document_count: int
    rebuilt_at_us: int
    hnsw_ready: bool

    def __post_init__(self) -> None:
        _canonical_model_id(self.model_id)
        _nonnegative_int(self.indexed_commit_seq, "indexed_commit_seq")
        _nonnegative_int(self.current_commit_seq, "current_commit_seq")
        _positive_int(self.dimensions, "dimensions")
        _nonnegative_int(self.document_count, "document_count")
        _nonnegative_int(self.rebuilt_at_us, "rebuilt_at_us")
        if not isinstance(self.hnsw_ready, bool):
            raise SemanticSearchError("hnsw_ready must be boolean.")

    @property
    def current(self) -> bool:
        return self.indexed_commit_seq >= self.current_commit_seq and self.hnsw_ready


@dataclass(frozen=True, slots=True)
class SemanticSearchResult:
    entity_id: uuid.UUID
    revision_id: uuid.UUID
    entity_type: SearchEntityType
    title: str | None
    text: str
    similarity: float
    contradiction_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.entity_id, uuid.UUID):
            raise TypeError("Semantic result entity_id must be a UUID.")
        if not isinstance(self.revision_id, uuid.UUID):
            raise TypeError("Semantic result revision_id must be a UUID.")
        if not isinstance(self.entity_type, SearchEntityType):
            raise TypeError("Semantic result entity_type must be a SearchEntityType.")
        if self.title is not None and not isinstance(self.title, str):
            raise TypeError("Semantic result title must be text or None.")
        if not isinstance(self.text, str):
            raise TypeError("Semantic result text must be text.")
        similarity = _finite_component(self.similarity)
        if not -1.0 <= similarity <= 1.0:
            raise SemanticSearchError("Semantic result similarity must be between -1 and 1.")
        _nonnegative_int(self.contradiction_count, "contradiction_count")


class LocalSemanticSearchService:
    """Maintain and query model-scoped semantic vectors as Derived State."""

    def __init__(
        self,
        database: SQLiteDatabase,
        provider: LMStudioEmbeddingProvider,
        *,
        batch_size: int = 32,
        hnsw_root: Path | None = None,
    ) -> None:
        if not isinstance(database, SQLiteDatabase):
            raise TypeError("database must be a SQLiteDatabase.")
        if not isinstance(provider, LMStudioEmbeddingProvider):
            raise TypeError("provider must be an LMStudioEmbeddingProvider.")
        validated_batch_size = _positive_int(batch_size, "batch_size")
        if hnsw_root is not None and not isinstance(hnsw_root, Path):
            raise TypeError("hnsw_root must be a pathlib.Path or None.")
        self.database = database
        self.provider = provider
        self.batch_size = validated_batch_size
        self.hnsw = HnswIndexStore(
            hnsw_root or (self.database.path.parent / "hnsw"),
            namespace="knowledge",
            reference_size=33,
        )

    def status(self, model_id: str) -> EmbeddingIndexStatus | None:
        normalized_model_id = _canonical_model_id(model_id)
        storage_model_id = _storage_model_id(normalized_model_id)
        row = self.database.connection.execute(
            """
            SELECT
                indexed_commit_seq,
                dimensions,
                document_count,
                rebuilt_at_us
            FROM search_embedding_state
            WHERE model_id = ?
            """,
            (storage_model_id,),
        ).fetchone()
        if row is None:
            return None
        indexed_commit_seq = _persisted_int(row["indexed_commit_seq"], "indexed_commit_seq")
        dimensions = _persisted_int(row["dimensions"], "dimensions", positive=True)
        document_count = _persisted_int(row["document_count"], "document_count")
        rebuilt_at_us = _persisted_int(row["rebuilt_at_us"], "rebuilt_at_us")
        current_commit_seq = _nonnegative_int(
            current_search_projection_commit_seq(self.database.connection),
            "current_commit_seq",
        )
        return EmbeddingIndexStatus(
            model_id=normalized_model_id,
            indexed_commit_seq=indexed_commit_seq,
            current_commit_seq=current_commit_seq,
            dimensions=dimensions,
            document_count=document_count,
            rebuilt_at_us=rebuilt_at_us,
            hnsw_ready=self.hnsw.ready(
                model_id=storage_model_id,
                snapshot=indexed_commit_seq,
                dimensions=dimensions,
                document_count=document_count,
            ),
        )

    def rebuild(self, model_id: str) -> EmbeddingIndexStatus:
        normalized_model_id = _canonical_model_id(model_id)
        storage_model_id = _storage_model_id(normalized_model_id)

        while True:
            self._ensure_fts_current()
            with self.database.write_transaction() as connection:
                current_commit_seq = _nonnegative_int(
                    current_search_projection_commit_seq(connection),
                    "current_commit_seq",
                )
                state = connection.execute(
                    """
                    SELECT indexed_commit_seq
                    FROM search_index_state
                    WHERE singleton_id = 1
                    """
                ).fetchone()
                if state is None:
                    raise SemanticSearchError("Search index state is missing.")
                search_index_seq = _persisted_int(
                    state["indexed_commit_seq"],
                    "search indexed_commit_seq",
                )
                if search_index_seq < current_commit_seq:
                    continue
                if search_index_seq > current_commit_seq:
                    raise SemanticSearchError(
                        "Search index watermark is ahead of canonical searchable state."
                    )
                source_rows = connection.execute(
                    """
                    SELECT entity_type, entity_id, revision_id, title, body
                    FROM search_fts
                    ORDER BY entity_type, entity_id, revision_id
                    """
                ).fetchall()
            break

        try:
            documents = [
                (
                    SearchEntityType(str(row["entity_type"])),
                    _uuid_from_hex(str(row["entity_id"])),
                    _uuid_from_hex(str(row["revision_id"])),
                    None if row["title"] in {None, ""} else str(row["title"]),
                    str(row["body"]),
                )
                for row in source_rows
            ]
        except ValueError as exc:
            raise SemanticSearchError("FTS index contains an invalid entity type.") from exc

        vectors: list[tuple[float, ...]] = []
        for start in range(0, len(documents), self.batch_size):
            batch = documents[start : start + self.batch_size]
            batch_vectors = self.provider.embed(
                model_id=normalized_model_id,
                texts=[
                    _prepare_document_text(normalized_model_id, document[4])
                    for document in batch
                ],
            )
            if len(batch_vectors) != len(batch):
                raise SemanticSearchError(
                    "Embedding provider returned an unexpected vector count."
                )
            vectors.extend(batch_vectors)

        dimensions = 1
        if vectors:
            dimensions = len(vectors[0])
            if dimensions <= 0:
                raise SemanticSearchError("Embedding vectors must not be empty.")
            if any(len(vector) != dimensions for vector in vectors):
                raise SemanticSearchError(
                    "Embedding model returned inconsistent dimensions."
                )

        normalized_vectors = [_normalize_vector(vector) for vector in vectors]

        with self.database.write_transaction() as connection:
            if current_search_projection_commit_seq(connection) != current_commit_seq:
                raise SemanticSearchError(
                    "Canonical state changed during embedding rebuild; retry required."
                )

            connection.execute(
                "DELETE FROM search_embeddings WHERE model_id IN (?, ?)",
                (storage_model_id, normalized_model_id),
            )
            connection.execute(
                "DELETE FROM search_embedding_state WHERE model_id = ?",
                (normalized_model_id,),
            )
            for document, vector in zip(documents, normalized_vectors, strict=True):
                entity_type, entity_id, revision_id, _title, text = document
                connection.execute(
                    """
                    INSERT INTO search_embeddings (
                        entity_type,
                        entity_id,
                        revision_id,
                        model_id,
                        dimensions,
                        vector_blob,
                        text_sha256,
                        created_at_us
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entity_type.value,
                        uuid_to_blob(entity_id),
                        uuid_to_blob(revision_id),
                        storage_model_id,
                        dimensions,
                        _pack_vector(vector),
                        hashlib.sha256(text.encode("utf-8")).digest(),
                        utc_now_us(),
                    ),
                )

            connection.execute(
                """
                INSERT INTO search_embedding_state (
                    model_id,
                    indexed_commit_seq,
                    dimensions,
                    document_count,
                    rebuilt_at_us
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(model_id) DO UPDATE SET
                    indexed_commit_seq = excluded.indexed_commit_seq,
                    dimensions = excluded.dimensions,
                    document_count = excluded.document_count,
                    rebuilt_at_us = excluded.rebuilt_at_us
                """,
                (
                    storage_model_id,
                    current_commit_seq,
                    dimensions,
                    len(documents),
                    utc_now_us(),
                ),
            )

        try:
            self._rebuild_hnsw_from_persisted(
                normalized_model_id,
                snapshot=current_commit_seq,
                dimensions=dimensions,
                document_count=len(documents),
            )
        except HnswIndexError as exc:
            raise SemanticSearchError(str(exc)) from exc

        status = self.status(normalized_model_id)
        if status is None or not status.current:
            raise SemanticSearchError("Embedding/HNSW index state was not published.")
        return status

    def ensure_current(self, model_id: str) -> EmbeddingIndexStatus:
        normalized_model_id = _canonical_model_id(model_id)
        status = self.status(normalized_model_id)
        current_commit_seq = _nonnegative_int(
            current_search_projection_commit_seq(self.database.connection),
            "current_commit_seq",
        )
        if status is None or status.indexed_commit_seq < current_commit_seq:
            return self.rebuild(normalized_model_id)
        if status.indexed_commit_seq > current_commit_seq:
            raise SemanticSearchError(
                "Semantic index watermark is ahead of canonical searchable state."
            )
        if not status.hnsw_ready:
            try:
                self._rebuild_hnsw_from_persisted(
                    normalized_model_id,
                    snapshot=status.indexed_commit_seq,
                    dimensions=status.dimensions,
                    document_count=status.document_count,
                )
            except HnswIndexError as exc:
                raise SemanticSearchError(str(exc)) from exc
            status = self.status(normalized_model_id)
            if status is None or not status.current:
                raise SemanticSearchError("HNSW sidecar rebuild did not become current.")
        return status

    def search(
        self,
        query: str,
        *,
        model_id: str,
        limit: int = 50,
    ) -> tuple[SemanticSearchResult, ...]:
        if not isinstance(query, str):
            raise SemanticSearchError("Semantic query must be text.")
        normalized_query = query.strip()
        if not normalized_query:
            raise SemanticSearchError("Semantic query must not be empty.")
        normalized_model_id = _canonical_model_id(model_id)
        validated_limit = _positive_int(limit, "Semantic search limit")
        if validated_limit > 500:
            raise SemanticSearchError("Semantic search limit must be between 1 and 500.")

        status = self.status(normalized_model_id)
        if status is None:
            raise SemanticSearchError(
                "Semantic index is absent; explicit rebuild required."
            )
        if status.indexed_commit_seq != status.current_commit_seq:
            raise SemanticSearchError(
                "Semantic index is stale or ahead; explicit rebuild/recovery required."
            )
        if not status.hnsw_ready:
            raise SemanticSearchError(
                "Semantic HNSW sidecar is unavailable; explicit maintenance required."
            )
        if status.document_count == 0:
            return ()

        storage_model_id = _storage_model_id(normalized_model_id)
        query_vectors = self.provider.embed(
            model_id=normalized_model_id,
            texts=[_prepare_query_text(normalized_model_id, normalized_query)],
        )
        if len(query_vectors) != 1:
            raise SemanticSearchError("Embedding provider did not return one query vector.")
        query_vector = _normalize_vector(query_vectors[0])
        if len(query_vector) != status.dimensions:
            raise SemanticSearchError(
                "Query embedding dimensions differ from the persisted index."
            )

        candidate_limit = min(
            status.document_count,
            max(validated_limit, min(500, validated_limit * 4)),
        )
        try:
            matches = self.hnsw.search(
                query_vector,
                model_id=storage_model_id,
                snapshot=status.indexed_commit_seq,
                dimensions=status.dimensions,
                document_count=status.document_count,
                limit=candidate_limit,
            )
        except HnswIndexError as exc:
            raise SemanticSearchError(str(exc)) from exc

        results: list[SemanticSearchResult] = []
        for match in matches:
            entity_type, entity_id, revision_id = _decode_reference(match.reference)
            row = self.database.connection.execute(
                """
                SELECT
                    e.vector_blob,
                    NULLIF(f.title, '') AS title,
                    f.body,
                    CASE
                        WHEN e.entity_type = 'claim' THEN (
                            SELECT count(*)
                            FROM claim_evidence AS ce
                            WHERE ce.claim_id = e.entity_id
                              AND ce.evidence_role = 'contradicts'
                        )
                        ELSE 0
                    END AS contradiction_count
                FROM search_embeddings AS e
                JOIN search_fts AS f
                  ON lower(hex(e.entity_id)) = f.entity_id
                 AND lower(hex(e.revision_id)) = f.revision_id
                 AND e.entity_type = f.entity_type
                WHERE e.model_id = ?
                  AND e.entity_type = ?
                  AND e.entity_id = ?
                  AND e.revision_id = ?
                """,
                (
                    storage_model_id,
                    entity_type.value,
                    uuid_to_blob(entity_id),
                    uuid_to_blob(revision_id),
                ),
            ).fetchone()
            if row is None:
                raise SemanticSearchError(
                    "HNSW candidate references missing persisted embedding state."
                )
            vector = _unpack_vector(bytes(row["vector_blob"]), status.dimensions)
            similarity = math.fsum(
                left * right for left, right in zip(query_vector, vector, strict=True)
            )
            if not math.isfinite(similarity):
                raise SemanticSearchError("Persisted embedding produced invalid similarity.")
            results.append(
                SemanticSearchResult(
                    entity_id=entity_id,
                    revision_id=revision_id,
                    entity_type=entity_type,
                    title=None if row["title"] is None else str(row["title"]),
                    text=str(row["body"]),
                    similarity=max(-1.0, min(1.0, similarity)),
                    contradiction_count=_persisted_int(
                        row["contradiction_count"],
                        "contradiction_count",
                    ),
                )
            )

        results.sort(
            key=lambda item: (
                -item.similarity,
                _SEMANTIC_TYPE_PRIORITY[item.entity_type],
                item.entity_id.hex,
            )
        )
        return tuple(results[:validated_limit])

    def _rebuild_hnsw_from_persisted(
        self,
        model_id: str,
        *,
        snapshot: int,
        dimensions: int,
        document_count: int,
    ) -> None:
        normalized_model_id = _canonical_model_id(model_id)
        validated_snapshot = _nonnegative_int(snapshot, "snapshot")
        validated_dimensions = _positive_int(dimensions, "dimensions")
        validated_document_count = _nonnegative_int(document_count, "document_count")
        storage_model_id = _storage_model_id(normalized_model_id)
        rows = self.database.connection.execute(
            """
            SELECT entity_type, entity_id, revision_id, vector_blob
            FROM search_embeddings
            WHERE model_id = ?
            ORDER BY entity_type, entity_id, revision_id
            """,
            (storage_model_id,),
        ).fetchall()
        if len(rows) != validated_document_count:
            raise SemanticSearchError(
                "Persisted embedding count disagrees with semantic index state."
            )
        entries_list: list[tuple[bytes, tuple[float, ...]]] = []
        for row in rows:
            try:
                entity_type = SearchEntityType(str(row["entity_type"]))
                entity_id = uuid.UUID(bytes=bytes(row["entity_id"]))
                revision_id = uuid.UUID(bytes=bytes(row["revision_id"]))
            except (TypeError, ValueError) as exc:
                raise SemanticSearchError(
                    "Persisted semantic reference identity is invalid."
                ) from exc
            entries_list.append(
                (
                    _encode_reference(entity_type, entity_id, revision_id),
                    _unpack_vector(bytes(row["vector_blob"]), validated_dimensions),
                )
            )
        self.hnsw.build(
            model_id=storage_model_id,
            snapshot=validated_snapshot,
            dimensions=validated_dimensions,
            entries=tuple(entries_list),
        )

    def _ensure_fts_current(self) -> None:
        from athena.retrieval.search import LocalSearchService

        LocalSearchService(self.database)._ensure_current()


_REFERENCE_TYPE_CODE = {
    SearchEntityType.KNOWLEDGE: 1,
    SearchEntityType.CLAIM: 2,
    SearchEntityType.CHAT_MESSAGE: 3,
}
_REFERENCE_CODE_TYPE = {value: key for key, value in _REFERENCE_TYPE_CODE.items()}


def _encode_reference(
    entity_type: SearchEntityType,
    entity_id: uuid.UUID,
    revision_id: uuid.UUID,
) -> bytes:
    if not isinstance(entity_type, SearchEntityType):
        raise SemanticSearchError("Semantic reference entity type is invalid.")
    if not isinstance(entity_id, uuid.UUID) or not isinstance(revision_id, uuid.UUID):
        raise SemanticSearchError("Semantic reference identities must be UUIDs.")
    return bytes((_REFERENCE_TYPE_CODE[entity_type],)) + entity_id.bytes + revision_id.bytes


def _decode_reference(value: bytes) -> tuple[SearchEntityType, uuid.UUID, uuid.UUID]:
    if not isinstance(value, bytes):
        raise SemanticSearchError("HNSW semantic reference must be bytes.")
    if len(value) != 33:
        raise SemanticSearchError("HNSW semantic reference has an invalid length.")
    try:
        entity_type = _REFERENCE_CODE_TYPE[value[0]]
    except KeyError as exc:
        raise SemanticSearchError("HNSW semantic reference has an invalid entity type.") from exc
    return entity_type, uuid.UUID(bytes=value[1:17]), uuid.UUID(bytes=value[17:33])


def _embedding_profile(model_id: str) -> str:
    normalized = _canonical_model_id(model_id).casefold()
    if "nomic-embed-text" in normalized:
        return "nomic-rag-v1"
    return "raw-rag-v1"


def _storage_model_id(model_id: str) -> str:
    normalized = _canonical_model_id(model_id)
    return f"{normalized}::athena-profile={_embedding_profile(normalized)}"


def _prepare_document_text(model_id: str, text: str) -> str:
    if not isinstance(text, str):
        raise SemanticSearchError("Semantic document text must be text.")
    if _embedding_profile(model_id) == "nomic-rag-v1":
        return f"search_document: {text}"
    return text


def _prepare_query_text(model_id: str, text: str) -> str:
    if not isinstance(text, str):
        raise SemanticSearchError("Semantic query text must be text.")
    if _embedding_profile(model_id) == "nomic-rag-v1":
        return f"search_query: {text}"
    return text


def _normalize_vector(vector: Sequence[float]) -> tuple[float, ...]:
    if isinstance(vector, (str, bytes, bytearray)):
        raise SemanticSearchError("Embedding vector must be a numeric sequence.")
    try:
        components = tuple(_finite_component(component) for component in vector)
    except TypeError as exc:
        raise SemanticSearchError("Embedding vector must be a numeric sequence.") from exc
    if not components:
        raise SemanticSearchError("Embedding vectors must not be empty.")
    norm = math.hypot(*components)
    if not math.isfinite(norm) or norm <= 0.0:
        raise SemanticSearchError("Embedding vector has zero or invalid magnitude.")
    return tuple(component / norm for component in components)


def _pack_vector(vector: Sequence[float]) -> bytes:
    normalized = tuple(_finite_component(component) for component in vector)
    if not normalized:
        raise SemanticSearchError("Embedding vectors must not be empty.")
    try:
        return struct.pack(f"<{len(normalized)}f", *normalized)
    except (OverflowError, struct.error) as exc:
        raise SemanticSearchError("Embedding vector cannot be persisted as float32.") from exc


def _unpack_vector(blob: bytes, dimensions: int) -> tuple[float, ...]:
    if not isinstance(blob, bytes):
        raise SemanticSearchError("Persisted embedding vector must be bytes.")
    validated_dimensions = _positive_int(dimensions, "dimensions")
    expected = validated_dimensions * 4
    if len(blob) != expected:
        raise SemanticSearchError("Persisted embedding vector has invalid length.")
    try:
        vector = tuple(struct.unpack(f"<{validated_dimensions}f", blob))
    except struct.error as exc:
        raise SemanticSearchError("Persisted embedding vector cannot be decoded.") from exc
    if any(not math.isfinite(component) for component in vector):
        raise SemanticSearchError("Persisted embedding vector contains non-finite values.")
    return vector


def _uuid_from_hex(value: str) -> uuid.UUID:
    if not isinstance(value, str):
        raise SemanticSearchError("FTS index UUID must be text.")
    try:
        return uuid.UUID(hex=value)
    except ValueError as exc:
        raise SemanticSearchError("FTS index contains an invalid UUID.") from exc
