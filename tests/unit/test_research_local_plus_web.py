from __future__ import annotations

import json
import uuid

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.research.service import ResearchConfigurationError


def test_local_plus_web_persists_truthful_authorized_capture_scope(tmp_path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start(run_startup_maintenance=False)
    authorization_id = uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b001")
    source_a = uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b010")
    source_b = uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b011")

    job = app.research.enqueue_local_plus_web(
        query="compare captured external evidence with local knowledge",
        authorization_id=authorization_id,
        captured_source_ids=(source_b, source_a, source_a),
    )

    persisted = app.jobs.get(job.job_id)
    requested = json.loads(persisted.requested_scope_json or "null")
    assert requested["mode"] == "local_plus_web"
    assert requested["explicit_source_ids"] == [
        str(source_a),
        str(source_b),
    ]
    assert requested["internet_scope"] == {
        "authorization_id": str(authorization_id),
        "captured_source_ids": [str(source_a), str(source_b)],
    }


def test_local_plus_web_fails_before_persistence_without_captured_sources(tmp_path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start(run_startup_maintenance=False)
    before = tuple(app.jobs.list(limit=500))

    with pytest.raises(
        ResearchConfigurationError,
        match="requires captured external Sources",
    ):
        app.research.enqueue_local_plus_web(
            query="web research",
            authorization_id=uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b001"),
            captured_source_ids=(),
        )

    assert tuple(app.jobs.list(limit=500)) == before


def test_local_plus_web_rejects_non_uuid_authorization_before_persistence(tmp_path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start(run_startup_maintenance=False)
    before = tuple(app.jobs.list(limit=500))

    with pytest.raises(
        ResearchConfigurationError,
        match="authorization_id UUID",
    ):
        app.research.enqueue_local_plus_web(
            query="web research",
            authorization_id="not-an-authorization",  # type: ignore[arg-type]
            captured_source_ids=(
                uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b010"),
            ),
        )

    assert tuple(app.jobs.list(limit=500)) == before
