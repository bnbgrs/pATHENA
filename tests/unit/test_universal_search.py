from __future__ import annotations

import sqlite3
import uuid

import pytest

from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType
from athena.retrieval.universal import (
    UniversalSearchEntityType,
    UniversalSearchError,
    UniversalSearchService,
)


class _Database:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE entity_registry (
                entity_id BLOB PRIMARY KEY,
                lifecycle_state TEXT NOT NULL
            );
            CREATE TABLE sources (
                source_id BLOB PRIMARY KEY,
                original_name TEXT,
                source_type TEXT NOT NULL,
                mime_type TEXT,
                source_uri TEXT,
                lifecycle_state TEXT NOT NULL
            );
            CREATE TABLE protected_sources (
                source_id BLOB PRIMARY KEY
            );
            CREATE TABLE jobs (
                job_id BLOB PRIMARY KEY,
                job_type TEXT NOT NULL,
                state TEXT NOT NULL,
                current_stage TEXT,
                blocked_reason TEXT,
                requested_scope_json TEXT,
                protection_scope_id BLOB,
                protected_payload_id BLOB
            );
            CREATE TABLE research_scopes (
                scope_id BLOB PRIMARY KEY,
                job_id BLOB NOT NULL,
                query_text TEXT NOT NULL
            );
            CREATE TABLE research_results (
                result_id BLOB PRIMARY KEY,
                scope_id BLOB NOT NULL,
                content_json TEXT NOT NULL
            );
            """
        )


class _RevisionedSearch:
    def __init__(self) -> None:
        self.calls: list[SearchEntityType] = []

    def search_lexical(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_type: SearchEntityType | None = None,
    ) -> tuple[HybridSearchResult, ...]:
        assert query == "alpha"
        assert entity_type is not None
        self.calls.append(entity_type)
        if entity_type is not SearchEntityType.KNOWLEDGE:
            return ()
        return (
            HybridSearchResult(
                entity_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                revision_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
                entity_type=SearchEntityType.KNOWLEDGE,
                title="Alpha handbook",
                text="Durable alpha guidance.",
                score=1.0,
                lexical_score=1.0,
                semantic_score=0.0,
                authority_score=1.0,
                contradiction_count=0,
                duplicate_count=0,
                retrieval_methods=("lexical",),
                rank=1,
            ),
        )


def _insert_rows(database: _Database) -> dict[str, uuid.UUID]:
    connection = database.connection
    ids = {
        "source": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "protected_source": uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "job": uuid.UUID("55555555-5555-5555-5555-555555555555"),
        "protected_job": uuid.UUID("66666666-6666-6666-6666-666666666666"),
        "scope": uuid.UUID("77777777-7777-7777-7777-777777777777"),
        "protected_scope": uuid.UUID("88888888-8888-8888-8888-888888888888"),
        "result": uuid.UUID("99999999-9999-9999-9999-999999999999"),
        "protected_result": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "protection": uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    }

    for key in ("source", "protected_source"):
        connection.execute(
            "INSERT INTO entity_registry(entity_id, lifecycle_state) VALUES (?, 'active')",
            (ids[key].bytes,),
        )

    connection.execute(
        """
        INSERT INTO sources(
            source_id, original_name, source_type, mime_type, source_uri, lifecycle_state
        ) VALUES (?, 'Alpha design.pdf', 'file', 'application/pdf', 'file:///alpha.pdf', 'active')
        """,
        (ids["source"].bytes,),
    )
    connection.execute(
        """
        INSERT INTO sources(
            source_id, original_name, source_type, mime_type, source_uri, lifecycle_state
        ) VALUES (?, 'Alpha secret.pdf', 'file', 'application/pdf', 'file:///secret.pdf', 'active')
        """,
        (ids["protected_source"].bytes,),
    )
    connection.execute(
        "INSERT INTO protected_sources(source_id) VALUES (?)",
        (ids["protected_source"].bytes,),
    )

    connection.execute(
        """
        INSERT INTO jobs(
            job_id, job_type, state, current_stage, blocked_reason,
            requested_scope_json, protection_scope_id, protected_payload_id
        ) VALUES (?, 'research.exhaustive', 'running', 'discovery', NULL,
                  '{"topic":"alpha"}', NULL, NULL)
        """,
        (ids["job"].bytes,),
    )
    connection.execute(
        """
        INSERT INTO jobs(
            job_id, job_type, state, current_stage, blocked_reason,
            requested_scope_json, protection_scope_id, protected_payload_id
        ) VALUES (?, 'research.exhaustive', 'running', 'discovery', NULL,
                  '{"topic":"alpha secret"}', ?, NULL)
        """,
        (ids["protected_job"].bytes, ids["protection"].bytes),
    )

    connection.execute(
        "INSERT INTO research_scopes(scope_id, job_id, query_text) VALUES (?, ?, 'Alpha study')",
        (ids["scope"].bytes, ids["job"].bytes),
    )
    connection.execute(
        "INSERT INTO research_scopes(scope_id, job_id, query_text) VALUES (?, ?, 'Alpha secret study')",
        (ids["protected_scope"].bytes, ids["protected_job"].bytes),
    )
    connection.execute(
        """
        INSERT INTO research_results(result_id, scope_id, content_json)
        VALUES (?, ?, '{"summary":"Alpha result synthesis"}')
        """,
        (ids["result"].bytes, ids["scope"].bytes),
    )
    connection.execute(
        """
        INSERT INTO research_results(result_id, scope_id, content_json)
        VALUES (?, ?, '{"summary":"Alpha protected synthesis"}')
        """,
        (ids["protected_result"].bytes, ids["protected_scope"].bytes),
    )
    connection.commit()
    return ids


def test_universal_search_combines_real_domains_and_excludes_protected_text() -> None:
    database = _Database()
    ids = _insert_rows(database)
    revisioned = _RevisionedSearch()
    service = UniversalSearchService(database, revisioned)  # type: ignore[arg-type]

    results = service.search("  alpha  ", limit=10)

    assert [item.rank for item in results] == list(range(1, len(results) + 1))
    assert {item.entity_type for item in results} == {
        UniversalSearchEntityType.KNOWLEDGE,
        UniversalSearchEntityType.SOURCE,
        UniversalSearchEntityType.RESEARCH_RESULT,
        UniversalSearchEntityType.JOB,
    }
    assert {item.result_ref for item in results} >= {
        "knowledge:11111111-1111-1111-1111-111111111111",
        f"source:{ids['source']}",
        f"research_result:{ids['result']}",
        f"job:{ids['job']}",
    }
    assert all(str(ids["protected_source"]) not in item.result_ref for item in results)
    assert all(str(ids["protected_job"]) not in item.result_ref for item in results)
    assert all(str(ids["protected_result"]) not in item.result_ref for item in results)

    operational = [
        item
        for item in results
        if item.entity_type
        in {
            UniversalSearchEntityType.SOURCE,
            UniversalSearchEntityType.RESEARCH_RESULT,
            UniversalSearchEntityType.JOB,
        }
    ]
    assert operational
    assert all(item.revision_id is None for item in operational)


def test_universal_search_filter_does_not_query_unselected_revisioned_domains() -> None:
    database = _Database()
    _insert_rows(database)
    revisioned = _RevisionedSearch()
    service = UniversalSearchService(database, revisioned)  # type: ignore[arg-type]

    results = service.search(
        "design alpha",
        entity_types=(UniversalSearchEntityType.SOURCE,),
    )

    assert revisioned.calls == []
    assert len(results) == 1
    assert results[0].entity_type is UniversalSearchEntityType.SOURCE


def test_universal_search_rejects_ambiguous_or_unbounded_filters() -> None:
    database = _Database()
    service = UniversalSearchService(
        database,
        _RevisionedSearch(),
    )  # type: ignore[arg-type]

    with pytest.raises(UniversalSearchError, match="must not be empty"):
        service.search("alpha", entity_types=())

    with pytest.raises(UniversalSearchError, match="duplicates"):
        service.search(
            "alpha",
            entity_types=(
                UniversalSearchEntityType.SOURCE,
                UniversalSearchEntityType.SOURCE,
            ),
        )

    with pytest.raises(UniversalSearchError, match="between 1 and 100"):
        service.search("alpha", limit=101)
