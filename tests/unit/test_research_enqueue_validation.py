from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
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


@pytest.mark.parametrize(
    "kwargs",
    (
        {"coverage_target": True},
        {"time_start_us": True},
        {"time_end_us": True},
        {"context_limit": True},
        {"output_reserve": True},
        {"safety_margin": False},
        {"max_hierarchy_depth": True},
    ),
)
def test_enqueue_rejects_boolean_numeric_fields_before_persistence(
    tmp_path: Path,
    kwargs: dict[str, Any],
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(ResearchConfigurationError):
            app.research.enqueue_local(query="Validate scalar types.", **kwargs)
        assert _research_job_count(app) == before
    finally:
        app.stop()


@pytest.mark.parametrize(
    "kwargs",
    (
        {"context_limit": "4096"},
        {"output_reserve": 1.5},
        {"safety_margin": "128"},
        {"max_hierarchy_depth": 2.5},
        {"coverage_target": "1.0"},
        {"requested_model_id": 123},
    ),
)
def test_enqueue_normalizes_invalid_scalar_types_to_configuration_errors(
    tmp_path: Path,
    kwargs: dict[str, Any],
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(ResearchConfigurationError):
            app.research.enqueue_local(query="Reject malformed inputs.", **kwargs)
        assert _research_job_count(app) == before
    finally:
        app.stop()


def test_enqueue_rejects_non_text_query_before_persistence(tmp_path: Path) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(ResearchConfigurationError, match="query must be text"):
            app.research.enqueue_local(query=object())  # type: ignore[arg-type]
        assert _research_job_count(app) == before
    finally:
        app.stop()


@pytest.mark.parametrize(
    "kwargs",
    (
        {"domains": (1,)},
        {"project_ids": ("not-a-uuid",)},
        {"source_types": ("file",)},
        {"explicit_source_ids": ("not-a-uuid",)},
    ),
)
def test_enqueue_rejects_invalid_filter_element_types_before_persistence(
    tmp_path: Path,
    kwargs: dict[str, Any],
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        before = _research_job_count(app)
        with pytest.raises(ResearchConfigurationError):
            app.research.enqueue_local(query="Reject malformed filters.", **kwargs)
        assert _research_job_count(app) == before
    finally:
        app.stop()


def test_enqueue_normalizes_integer_coverage_to_float_and_initializes(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        job = app.research.enqueue_local(
            query="  Normalized research query.  ",
            coverage_target=1,
        )
        requested = json.loads(job.requested_scope_json or "null")
        assert requested["query"] == "Normalized research query."
        assert requested["coverage_target"] == 1.0
        assert isinstance(requested["coverage_target"], float)

        scope = app.research.initialize(job.job_id)
        assert scope.query_text == "Normalized research query."
        assert scope.coverage_target == 1.0
    finally:
        app.stop()
