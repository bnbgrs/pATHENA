"""One local universal-search contract across user-visible pATHENA domains.

The service deliberately reuses the established lexical retrieval path for
revisioned Knowledge/Claim/Chat content and reads operational or immutable
records from their canonical SQLite tables. It does not maintain a second
desktop index and it never exposes protected Source, Research, or Job text.
"""

from __future__ import annotations

import json
import math
import sqlite3
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType
from athena.storage.database import SQLiteDatabase


class UniversalSearchError(ValueError):
    """Raised when a universal-search request is invalid."""


class UniversalSearchEntityType(str, Enum):
    """Stable filter/result taxonomy exposed by the Core universal search."""

    KNOWLEDGE = "knowledge"
    CLAIM = "claim"
    CHAT_MESSAGE = "chat_message"
    RESEARCH_RESULT = "research_result"
    SOURCE = "source"
    JOB = "job"


@dataclass(frozen=True, slots=True)
class UniversalSearchResult:
    """One stable local result with an optional canonical revision identity."""

    result_ref: str
    entity_id: uuid.UUID
    revision_id: uuid.UUID | None
    entity_type: UniversalSearchEntityType
    title: str | None
    preview: str
    rank: int
    retrieval_methods: tuple[str, ...] = ("lexical",)

    def __post_init__(self) -> None:
        if not isinstance(self.result_ref, str) or not self.result_ref.strip():
            raise TypeError("Universal search result_ref must be non-empty text.")
        if not isinstance(self.entity_id, uuid.UUID):
            raise TypeError("Universal search entity_id must be a UUID.")
        if self.revision_id is not None and not isinstance(self.revision_id, uuid.UUID):
            raise TypeError("Universal search revision_id must be a UUID or None.")
        if not isinstance(self.entity_type, UniversalSearchEntityType):
            raise TypeError(
                "Universal search entity_type must be a UniversalSearchEntityType."
            )
        if self.title is not None and not isinstance(self.title, str):
            raise TypeError("Universal search title must be text or None.")
        if not isinstance(self.preview, str):
            raise TypeError("Universal search preview must be text.")
        if isinstance(self.rank, bool) or not isinstance(self.rank, int) or self.rank < 1:
            raise ValueError("Universal search rank must be a positive integer.")
        if self.retrieval_methods != ("lexical",):
            raise ValueError(
                "Universal local search currently supports lexical retrieval only."
            )


@dataclass(frozen=True, slots=True)
class _Candidate:
    result_ref: str
    entity_id: uuid.UUID
    revision_id: uuid.UUID | None
    entity_type: UniversalSearchEntityType
    title: str | None
    preview: str
    relevance: float


class LexicalRevisionedSearch(Protocol):
    """Existing lexical path used for Knowledge, Claims, and Chat messages."""

    def search_lexical(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_type: SearchEntityType | None = None,
    ) -> tuple[HybridSearchResult, ...]: ...


_CANONICAL_TYPES: tuple[
    tuple[UniversalSearchEntityType, SearchEntityType],
    ...,
] = (
    (UniversalSearchEntityType.KNOWLEDGE, SearchEntityType.KNOWLEDGE),
    (UniversalSearchEntityType.CLAIM, SearchEntityType.CLAIM),
    (UniversalSearchEntityType.CHAT_MESSAGE, SearchEntityType.CHAT_MESSAGE),
)

_TYPE_ORDER = {
    entity_type: index
    for index, entity_type in enumerate(UniversalSearchEntityType)
}


class UniversalSearchService:
    """Search six persisted pATHENA domains through one deterministic contract."""

    def __init__(
        self,
        database: SQLiteDatabase,
        revisioned_search: LexicalRevisionedSearch,
    ) -> None:
        self.database = database
        self.revisioned_search = revisioned_search

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[UniversalSearchResult, ...]:
        normalized_query = _query_text(query)
        validated_limit = _limit(limit)
        selected_types = _entity_filter(entity_types)
        candidates: list[_Candidate] = []

        for universal_type, search_type in _CANONICAL_TYPES:
            if universal_type not in selected_types:
                continue
            results = self.revisioned_search.search_lexical(
                normalized_query,
                limit=min(200, max(validated_limit * 4, 20)),
                entity_type=search_type,
            )
            candidates.extend(
                _revisioned_candidate(universal_type, result, normalized_query)
                for result in results
            )

        connection = self.database.connection
        if UniversalSearchEntityType.SOURCE in selected_types:
            candidates.extend(
                self._search_sources(connection, normalized_query, validated_limit)
            )
        if UniversalSearchEntityType.RESEARCH_RESULT in selected_types:
            candidates.extend(
                self._search_research_results(
                    connection, normalized_query, validated_limit
                )
            )
        if UniversalSearchEntityType.JOB in selected_types:
            candidates.extend(
                self._search_jobs(connection, normalized_query, validated_limit)
            )

        ordered = sorted(
            candidates,
            key=lambda item: (
                -item.relevance,
                _TYPE_ORDER[item.entity_type],
                item.result_ref,
            ),
        )[:validated_limit]
        return tuple(
            UniversalSearchResult(
                result_ref=item.result_ref,
                entity_id=item.entity_id,
                revision_id=item.revision_id,
                entity_type=item.entity_type,
                title=item.title,
                preview=item.preview,
                rank=rank,
            )
            for rank, item in enumerate(ordered, start=1)
        )

    @staticmethod
    def _search_sources(
        connection: sqlite3.Connection,
        query: str,
        limit: int,
    ) -> tuple[_Candidate, ...]:
        rows = connection.execute(
            """
            SELECT
                s.source_id,
                s.original_name,
                s.source_type,
                s.mime_type,
                s.source_uri
            FROM sources AS s
            JOIN entity_registry AS entity
              ON entity.entity_id = s.source_id
            LEFT JOIN protected_sources AS protected
              ON protected.source_id = s.source_id
            WHERE entity.lifecycle_state != 'deleted'
              AND s.lifecycle_state != 'deleted'
              AND protected.source_id IS NULL
              AND instr(
                    lower(
                        coalesce(s.original_name, '') || ' ' ||
                        coalesce(s.source_type, '') || ' ' ||
                        coalesce(s.mime_type, '') || ' ' ||
                        coalesce(s.source_uri, '')
                    ),
                    lower(?)
                  ) > 0
            ORDER BY s.source_id ASC
            LIMIT ?
            """,
            (query, min(400, max(limit * 8, 40))),
        ).fetchall()
        output: list[_Candidate] = []
        for row in rows:
            entity_id = _uuid_blob(row["source_id"], "Source source_id")
            title = _optional_text(row["original_name"])
            body = " · ".join(
                value
                for value in (
                    _optional_text(row["source_type"]),
                    _optional_text(row["mime_type"]),
                    _optional_text(row["source_uri"]),
                )
                if value
            )
            output.append(
                _Candidate(
                    result_ref=f"source:{entity_id}",
                    entity_id=entity_id,
                    revision_id=None,
                    entity_type=UniversalSearchEntityType.SOURCE,
                    title=title,
                    preview=_preview(body or title or "Source"),
                    relevance=_relevance(query, title, body),
                )
            )
        return tuple(output)

    @staticmethod
    def _search_research_results(
        connection: sqlite3.Connection,
        query: str,
        limit: int,
    ) -> tuple[_Candidate, ...]:
        rows = connection.execute(
            """
            SELECT
                result.result_id,
                scope.query_text,
                result.content_json
            FROM research_results AS result
            JOIN research_scopes AS scope
              ON scope.scope_id = result.scope_id
            JOIN jobs AS job
              ON job.job_id = scope.job_id
            WHERE job.protection_scope_id IS NULL
              AND job.protected_payload_id IS NULL
              AND instr(
                    lower(scope.query_text || ' ' || result.content_json),
                    lower(?)
                  ) > 0
            ORDER BY result.result_id ASC
            LIMIT ?
            """,
            (query, min(400, max(limit * 8, 40))),
        ).fetchall()
        output: list[_Candidate] = []
        for row in rows:
            entity_id = _uuid_blob(row["result_id"], "Research result_id")
            title = _optional_text(row["query_text"])
            content = _json_preview(_optional_text(row["content_json"]) or "")
            output.append(
                _Candidate(
                    result_ref=f"research_result:{entity_id}",
                    entity_id=entity_id,
                    revision_id=None,
                    entity_type=UniversalSearchEntityType.RESEARCH_RESULT,
                    title=title,
                    preview=_preview(content or title or "Research result"),
                    relevance=_relevance(query, title, content),
                )
            )
        return tuple(output)

    @staticmethod
    def _search_jobs(
        connection: sqlite3.Connection,
        query: str,
        limit: int,
    ) -> tuple[_Candidate, ...]:
        rows = connection.execute(
            """
            SELECT
                job_id,
                job_type,
                state,
                current_stage,
                blocked_reason,
                requested_scope_json
            FROM jobs
            WHERE protection_scope_id IS NULL
              AND protected_payload_id IS NULL
              AND instr(
                    lower(
                        job_type || ' ' ||
                        state || ' ' ||
                        coalesce(current_stage, '') || ' ' ||
                        coalesce(blocked_reason, '') || ' ' ||
                        coalesce(requested_scope_json, '')
                    ),
                    lower(?)
                  ) > 0
            ORDER BY job_id ASC
            LIMIT ?
            """,
            (query, min(400, max(limit * 8, 40))),
        ).fetchall()
        output: list[_Candidate] = []
        for row in rows:
            entity_id = _uuid_blob(row["job_id"], "Job job_id")
            job_type = _optional_text(row["job_type"]) or "Job"
            state = _optional_text(row["state"]) or ""
            stage = _optional_text(row["current_stage"]) or ""
            blocked = _optional_text(row["blocked_reason"]) or ""
            scope = _json_preview(_optional_text(row["requested_scope_json"]) or "")
            body = " · ".join(
                value for value in (state, stage, blocked, scope) if value
            )
            output.append(
                _Candidate(
                    result_ref=f"job:{entity_id}",
                    entity_id=entity_id,
                    revision_id=None,
                    entity_type=UniversalSearchEntityType.JOB,
                    title=job_type,
                    preview=_preview(body or job_type),
                    relevance=_relevance(query, job_type, body),
                )
            )
        return tuple(output)


def _query_text(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("Universal search query must be text.")
    normalized = " ".join(value.split())
    if not normalized:
        raise UniversalSearchError("Universal search query must not be empty.")
    if len(normalized) > 512:
        raise UniversalSearchError(
            "Universal search query must not exceed 512 characters."
        )
    return normalized


def _limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Universal search limit must be an integer.")
    if not 1 <= value <= 100:
        raise UniversalSearchError("Universal search limit must be between 1 and 100.")
    return value


def _entity_filter(
    value: tuple[UniversalSearchEntityType, ...] | None,
) -> frozenset[UniversalSearchEntityType]:
    if value is None:
        return frozenset(UniversalSearchEntityType)
    if not isinstance(value, tuple):
        raise TypeError("Universal search entity_types must be a tuple or None.")
    if not value:
        raise UniversalSearchError("Universal search entity_types must not be empty.")
    if any(not isinstance(item, UniversalSearchEntityType) for item in value):
        raise TypeError(
            "Universal search entity_types must contain UniversalSearchEntityType values."
        )
    if len(set(value)) != len(value):
        raise UniversalSearchError(
            "Universal search entity_types must not contain duplicates."
        )
    return frozenset(value)


def _revisioned_candidate(
    entity_type: UniversalSearchEntityType,
    result: HybridSearchResult,
    query: str,
) -> _Candidate:
    return _Candidate(
        result_ref=f"{entity_type.value}:{result.entity_id}",
        entity_id=result.entity_id,
        revision_id=result.revision_id,
        entity_type=entity_type,
        title=result.title,
        preview=_preview(result.text),
        relevance=_relevance(query, result.title, result.text),
    )


def _uuid_blob(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{label} must be persisted as BLOB bytes.")
    raw = bytes(value)
    if len(raw) != 16:
        raise ValueError(f"{label} must contain exactly 16 bytes.")
    return uuid.UUID(bytes=raw)


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("Universal search persisted text must be TEXT or NULL.")
    return value


def _json_preview(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return value
    flattened: list[str] = []
    _collect_json_text(parsed, flattened)
    return " ".join(flattened)


def _collect_json_text(value: object, output: list[str]) -> None:
    if len(output) >= 40:
        return
    if isinstance(value, str):
        text = " ".join(value.split())
        if text:
            output.append(text)
        return
    if isinstance(value, dict):
        for key in sorted(value):
            _collect_json_text(value[key], output)
        return
    if isinstance(value, list):
        for item in value:
            _collect_json_text(item, output)
        return
    if value is not None and not isinstance(value, (bytes, bytearray)):
        output.append(str(value))


def _preview(value: str, *, limit: int = 320) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _relevance(query: str, title: str | None, body: str) -> float:
    needle = query.casefold()
    title_text = (title or "").casefold()
    body_text = body.casefold()

    score = 0.0
    if title_text == needle:
        score += 8.0
    elif title_text.startswith(needle):
        score += 5.0
    elif needle in title_text:
        score += 3.0

    if needle in body_text:
        score += 1.0
        occurrences = body_text.count(needle)
        score += min(2.0, math.log2(max(1, occurrences)) * 0.25)

    return score
