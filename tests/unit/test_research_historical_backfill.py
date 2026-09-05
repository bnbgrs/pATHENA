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
