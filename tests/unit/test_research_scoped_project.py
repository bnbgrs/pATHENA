from __future__ import annotations

import json
import uuid
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
    return sum(
        job.job_type == "research.exhaustive"
        for job in app.jobs.list(limit=500)
    )


def test_scoped_project_persists_truthful_mode_and_project_scope(tmp_path: Path) -> None:
    app = _app(tmp_path / "runtime")
    try:
        project_a = uuid.UUID("00000000-0000-0000-0000-000000000001")
        project_b = uuid.UUID("00000000-0000-0000-0000-000000000002")
        job = app.research.enqueue_scoped_project(
            query="  Research only these projects.  ",
            project_ids=(project_b, project_a, project_b),
            coverage_target=1,
        )

        requested = json.loads(job.requested_scope_json or "null")
        assert requested["mode"] == ResearchMode.SCOPED_PROJECT.value
        assert requested["query"] == "Research only these projects."
        assert requested["project_ids"] == [str(project_a), str(project_b)]
        assert requested["internet_scope"] is None

        scope = app.research.initialize(job.job_id)
        assert scope.mode is ResearchMode.SCOPED_PROJECT
        assert json.loads(scope.project_ids_json) == [str(project_a), str(project_b)]
        assert scope.snapshot_commit_seq >= 0
    finally:
        app.stop()


def test_scoped_project_rejects_empty_project_scope_before_persistence(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(
            ResearchConfigurationError,
            match="requires at least one project_id",
        ):
            app.research.enqueue_scoped_project(
                query="This must not become an unscoped research job.",
                project_ids=(),
            )
        assert _research_job_count(app) == before
    finally:
        app.stop()
