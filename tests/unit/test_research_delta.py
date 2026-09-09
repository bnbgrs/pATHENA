from __future__ import annotations

import json
from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.research.delta import enqueue_delta
from athena.research.models import ResearchMode
from athena.research.service import ResearchConfigurationError


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def _capture(app: AthenaApplication, path: Path, text: str):
    path.write_text(text, encoding="utf-8", newline="")
    return app.sources.capture_file(path).source


def _research_job_count(app: AthenaApplication) -> int:
    return sum(job.job_type == "research.exhaustive" for job in app.jobs.list(limit=500))


def test_delta_research_freezes_only_new_explicit_sources(tmp_path: Path) -> None:
    app = _app(tmp_path / "runtime")
    try:
        original = _capture(app, tmp_path / "original.txt", "original snapshot evidence")
        baseline_job = app.research.enqueue_local(query="Establish the original snapshot.")
        baseline_scope = app.research.initialize(baseline_job.job_id)

        delta_source = _capture(app, tmp_path / "delta.txt", "newly relevant delta evidence")
        delta_job = enqueue_delta(
            app.research,
            query="Check the newly relevant evidence.",
            explicit_source_ids=(delta_source.source_id,),
        )
        requested = json.loads(delta_job.requested_scope_json or "null")
        delta_scope = app.research.initialize(delta_job.job_id)
        app.research.freeze_candidates(delta_job.job_id)
        candidates = app.research_repository.list_candidates(delta_scope.scope_id)

        assert requested["mode"] == ResearchMode.DELTA.value
        assert requested["explicit_source_ids"] == [str(delta_source.source_id)]
        assert delta_scope.mode is ResearchMode.DELTA
        assert delta_scope.snapshot_commit_seq > baseline_scope.snapshot_commit_seq
        assert [candidate.source_id for candidate in candidates] == [delta_source.source_id]
        assert original.source_id not in {candidate.source_id for candidate in candidates}
    finally:
        app.stop()


def test_delta_research_rejects_empty_source_set_before_persistence(tmp_path: Path) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(
            ResearchConfigurationError,
            match="requires at least one captured Source",
        ):
            enqueue_delta(
                app.research,
                query="Do not create an ungrounded delta.",
                explicit_source_ids=(),
            )
        assert _research_job_count(app) == before
    finally:
        app.stop()
