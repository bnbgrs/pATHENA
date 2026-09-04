from __future__ import annotations

import sqlite3
import uuid

from athena.common.ids import uuid_to_blob
from athena.research import repository as repository_module
from athena.research.coverage import ResearchCoverage
from athena.research.repository import ResearchRepository


def test_scope_counter_recompute_delegates_to_canonical_coverage(monkeypatch) -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE research_candidate_sets (
            candidate_set_id BLOB PRIMARY KEY,
            scope_id BLOB NOT NULL
        );
        CREATE TABLE research_candidates (
            candidate_set_id BLOB NOT NULL,
            eligibility_state TEXT NOT NULL
        );
        CREATE TABLE research_work_items (
            scope_id BLOB NOT NULL,
            state TEXT NOT NULL
        );
        CREATE TABLE research_scopes (
            scope_id BLOB PRIMARY KEY,
            candidate_total INTEGER NOT NULL DEFAULT 0,
            processed_count INTEGER NOT NULL DEFAULT 0,
            successful_count INTEGER NOT NULL DEFAULT 0,
            irrelevant_count INTEGER NOT NULL DEFAULT 0,
            failed_count INTEGER NOT NULL DEFAULT 0,
            unavailable_count INTEGER NOT NULL DEFAULT 0,
            excluded_count INTEGER NOT NULL DEFAULT 0,
            coverage_ratio REAL NOT NULL DEFAULT 0.0,
            updated_at_us INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    scope_id = uuid.uuid4()
    candidate_set_id = uuid.uuid4()
    scope_blob = uuid_to_blob(scope_id)
    connection.execute(
        "INSERT INTO research_candidate_sets (candidate_set_id, scope_id) VALUES (?, ?)",
        (uuid_to_blob(candidate_set_id), scope_blob),
    )
    connection.execute(
        "INSERT INTO research_scopes (scope_id) VALUES (?)",
        (scope_blob,),
    )
    for state in ("eligible", "eligible", "eligible", "eligible", "excluded_duplicate"):
        connection.execute(
            "INSERT INTO research_candidates (candidate_set_id, eligibility_state) VALUES (?, ?)",
            (uuid_to_blob(candidate_set_id), state),
        )
    for state in ("successful", "irrelevant", "failed", "unavailable"):
        connection.execute(
            "INSERT INTO research_work_items (scope_id, state) VALUES (?, ?)",
            (scope_blob, state),
        )

    captured: list[ResearchCoverage] = []

    def accounting(**kwargs: int) -> ResearchCoverage:
        result = ResearchCoverage(**kwargs)
        captured.append(result)
        return result

    monkeypatch.setattr(repository_module, "CoverageAccounting", accounting)
    ResearchRepository._recompute_scope_counters(
        connection,
        scope_id=scope_id,
        now_us=123,
    )

    assert len(captured) == 1
    assert captured[0].eligible_count == 4
    assert captured[0].processed_count == 4
    assert captured[0].coverage_ratio == 0.5
    row = connection.execute(
        "SELECT processed_count, coverage_ratio, updated_at_us FROM research_scopes WHERE scope_id = ?",
        (scope_blob,),
    ).fetchone()
    assert row is not None
    assert int(row["processed_count"]) == 4
    assert float(row["coverage_ratio"]) == 0.5
    assert int(row["updated_at_us"]) == 123
