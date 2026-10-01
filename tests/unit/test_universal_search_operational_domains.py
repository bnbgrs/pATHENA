from __future__ import annotations

import hashlib
import json
from pathlib import Path

from athena.common.ids import new_uuid7
from athena.common.time import utc_now_us
from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.retrieval.search import SearchEntityType


def _started_app(tmp_path: Path) -> AthenaApplication:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=tmp_path / "runtime",
        )
    )
    app.start()
    return app


def _insert_research_result(
    app: AthenaApplication,
    *,
    scope_id,
    summary: str,
):
    scope = app.research_repository.get_scope(scope_id)
    result_id = new_uuid7()
    content_json = json.dumps(
        {
            "summary": summary,
            "findings": ["Orion evidence remains durable."],
            "contradictions": [],
            "uncertainty": "bounded",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with app.database.write_transaction() as connection:
        connection.execute(
            """
            INSERT INTO research_results (
                result_id,
                scope_id,
                final_artifact_id,
                content_json,
                content_hash,
                snapshot_commit_seq,
                model_signature_id,
                synthesis_pipeline_version,
                candidate_total,
                processed_count,
                successful_count,
                irrelevant_count,
                failed_count,
                unavailable_count,
                excluded_count,
                coverage_ratio,
                problem_sources_json,
                created_at_us
            ) VALUES (?, ?, NULL, ?, ?, ?, NULL, ?, 0, 0, 0, 0, 0, 0, 0, 1.0, '[]', ?)
            """,
            (
                result_id.bytes,
                scope.scope_id.bytes,
                content_json,
                hashlib.sha256(content_json.encode("utf-8")).digest(),
                scope.snapshot_commit_seq,
                "test-universal-search",
                utc_now_us(),
            ),
        )
    return result_id


def test_local_search_includes_live_research_source_and_job_domains(tmp_path: Path) -> None:
    app = _started_app(tmp_path)
    try:
        source_path = tmp_path / "Orion field notes.txt"
        source_path.write_text("Captured content is retained separately.", encoding="utf-8")
        source = app.sources.capture_file(source_path).source

        job = app.research.enqueue_local(query="Orion durable synthesis")
        scope = app.research.initialize(job.job_id)
        result_id = _insert_research_result(
            app,
            scope_id=scope.scope_id,
            summary="Orion research summary",
        )

        results = app.search.search("Orion", limit=20)
        by_type = {item.entity_type: item for item in results}

        assert by_type[SearchEntityType.SOURCE].entity_id == source.source_id
        assert by_type[SearchEntityType.JOB].entity_id == job.job_id
        assert by_type[SearchEntityType.RESEARCH_RESULT].entity_id == result_id
        assert all(
            by_type[entity_type].revision_id is None
            for entity_type in (
                SearchEntityType.SOURCE,
                SearchEntityType.JOB,
                SearchEntityType.RESEARCH_RESULT,
            )
        )
    finally:
        app.stop()


def test_core_search_operational_filter_is_lexical_and_needs_no_embedding_server(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)
    try:
        job = app.research.enqueue_local(query="Orion lexical-only operational search")

        response = app.api.search(
            "Orion",
            model_id="embedding-server-must-not-be-called",
            entity_type=SearchEntityType.JOB,
        )

        assert len(response) == 1
        item = response[0]
        assert item.result_ref == f"job:{job.job_id}"
        assert item.entity_type == "job"
        assert item.revision_id is None
        assert item.retrieval_methods == ("lexical",)
        assert item.protection.state == "unprotected"
    finally:
        app.stop()
