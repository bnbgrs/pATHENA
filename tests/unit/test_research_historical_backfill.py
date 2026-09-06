from __future__ import annotations

import json
from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.research.models import ResearchMode
from athena.research.service import ResearchConfigurationError


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def _research_job_count(app: AthenaApplication) -> int:
    return sum(job.job_type == "research.exhaustive" for job in app.jobs.list(limit=500))


def _capture_source_at(
    app: AthenaApplication,
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    name: str,
    acquired_at_us: int,
) -> object:
    path = root / name
    path.write_text(f"historical source {name}\n", encoding="utf-8")
    monkeypatch.setattr(
        "athena.source.repository.utc_now_us",
        lambda: acquired_at_us,
    )
    return app.sources.capture_file(path).source.source_id


def test_historical_backfill_persists_truthful_mode_and_time_scope(tmp_path: Path) -> None:
    app = _app(tmp_path / "runtime")
    try:
        job = app.research.enqueue_historical_backfill(
            query="  Backfill this historical interval.  ",
            time_start_us=1_700_000_000_000_000,
            time_end_us=1_710_000_000_000_000,
            coverage_target=1,
        )

        requested = json.loads(job.requested_scope_json or "null")
        assert requested["mode"] == ResearchMode.HISTORICAL_BACKFILL.value
        assert requested["query"] == "Backfill this historical interval."
        assert requested["time_start_us"] == 1_700_000_000_000_000
        assert requested["time_end_us"] == 1_710_000_000_000_000
        assert requested["internet_scope"] is None

        scope = app.research.initialize(job.job_id)
        assert scope.mode is ResearchMode.HISTORICAL_BACKFILL
        assert scope.time_start_us == 1_700_000_000_000_000
        assert scope.time_end_us == 1_710_000_000_000_000
        assert scope.internet_scope_json is None
        assert scope.snapshot_commit_seq >= 0
    finally:
        app.stop()


def test_historical_backfill_candidate_freeze_preserves_truthful_mode(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        job = app.research.enqueue_historical_backfill(
            query="Freeze only the bounded historical snapshot.",
            time_start_us=1_700_000_000_000_000,
            time_end_us=1_710_000_000_000_000,
            coverage_target=1,
        )
        scope = app.research.initialize(job.job_id)

        candidate_set = app.research.repository.freeze_local_candidates(scope.scope_id)

        persisted = app.research.repository.get_scope(scope.scope_id)
        assert persisted.mode is ResearchMode.HISTORICAL_BACKFILL
        assert persisted.time_start_us == 1_700_000_000_000_000
        assert persisted.time_end_us == 1_710_000_000_000_000
        assert candidate_set.snapshot_commit_seq == persisted.snapshot_commit_seq
        assert candidate_set.candidate_total == 0
    finally:
        app.stop()


def test_historical_backfill_freeze_honors_inclusive_time_and_pinned_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app(tmp_path / "runtime")
    source_root = tmp_path / "sources"
    source_root.mkdir()
    try:
        below = _capture_source_at(
            app,
            source_root,
            monkeypatch,
            name="below.txt",
            acquired_at_us=99,
        )
        lower = _capture_source_at(
            app,
            source_root,
            monkeypatch,
            name="lower.txt",
            acquired_at_us=100,
        )
        upper = _capture_source_at(
            app,
            source_root,
            monkeypatch,
            name="upper.txt",
            acquired_at_us=200,
        )
        above = _capture_source_at(
            app,
            source_root,
            monkeypatch,
            name="above.txt",
            acquired_at_us=201,
        )

        job = app.research.enqueue_historical_backfill(
            query="Freeze only sources visible inside the pinned historical interval.",
            time_start_us=100,
            time_end_us=200,
            coverage_target=1,
        )
        scope = app.research.initialize(job.job_id)

        late = _capture_source_at(
            app,
            source_root,
            monkeypatch,
            name="late.txt",
            acquired_at_us=150,
        )

        candidate_set = app.research.repository.freeze_local_candidates(scope.scope_id)
        candidates = app.research.repository.list_candidates(scope.scope_id)
        selected = {candidate.source_id for candidate in candidates}

        assert candidate_set.snapshot_commit_seq == scope.snapshot_commit_seq
        assert candidate_set.candidate_total == 2
        assert selected == {lower, upper}
        assert selected.isdisjoint({below, above, late})
    finally:
        app.stop()


def test_historical_backfill_rejects_invalid_bounds_before_persistence(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(
            ResearchConfigurationError,
            match="time_end_us must be >= time_start_us",
        ):
            app.research.enqueue_historical_backfill(
                query="This invalid interval must not be persisted.",
                time_start_us=20,
                time_end_us=10,
            )
        assert _research_job_count(app) == before
    finally:
        app.stop()


def test_historical_backfill_rejects_non_integer_bounds_before_persistence(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(
            ResearchConfigurationError,
            match="requires non-negative integer time bounds",
        ):
            app.research.enqueue_historical_backfill(
                query="This malformed interval must not be persisted.",
                time_start_us=True,
                time_end_us=10,
            )
        assert _research_job_count(app) == before
    finally:
        app.stop()
