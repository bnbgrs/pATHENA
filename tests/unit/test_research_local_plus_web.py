from __future__ import annotations

import json
import uuid

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.external.gateway import ExternalResponse
from athena.research.errors import ResearchSnapshotError
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

class _StaticExternalTransport:
    def fetch(self, url: str, *, max_bytes: int, timeout_seconds: float) -> ExternalResponse:
        del max_bytes, timeout_seconds
        return ExternalResponse(
            final_url=url,
            status=200,
            headers={"content-type": "text/plain"},
            body=f"captured external evidence: {url}".encode(),
        )


def _capture_local(app: AthenaApplication, tmp_path, name: str, body: str) -> uuid.UUID:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return app.sources.capture_file(path).source.source_id


def test_local_plus_web_freeze_unions_pinned_local_with_only_authorized_capture(
    tmp_path,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start(run_startup_maintenance=False)
    try:
        app.external_access.transports["direct_explicit"] = _StaticExternalTransport()
        local_source = _capture_local(app, tmp_path, "local.txt", "local evidence")

        authorization = app.external_access.authorize_explicit(
            purpose="focused Local+Web research",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )
        authorized_external = app.external_access.capture_url(
            authorization.authorization_id,
            "https://example.com/authorized",
        ).source.source_id

        other_authorization = app.external_access.authorize_explicit(
            purpose="unrelated historical capture",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )
        unrelated_external = app.external_access.capture_url(
            other_authorization.authorization_id,
            "https://example.com/unrelated",
        ).source.source_id

        job = app.research.enqueue_local_plus_web(
            query="union local evidence with only this authorized capture",
            authorization_id=authorization.authorization_id,
            captured_source_ids=(authorized_external,),
        )
        scope = app.research.initialize(job.job_id)
        late_local = _capture_local(app, tmp_path, "late.txt", "late local evidence")

        candidate_set = app.research.repository.freeze_local_candidates(scope.scope_id)
        candidates = app.research.repository.list_candidates(scope.scope_id)
        selected = {candidate.source_id for candidate in candidates}

        assert candidate_set.snapshot_commit_seq == scope.snapshot_commit_seq
        assert selected == {local_source, authorized_external}
        assert selected.isdisjoint({unrelated_external, late_local})
    finally:
        app.stop()


def test_local_plus_web_freeze_fails_closed_on_mismatched_capture_linkage(tmp_path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start(run_startup_maintenance=False)
    try:
        app.external_access.transports["direct_explicit"] = _StaticExternalTransport()
        authorization = app.external_access.authorize_explicit(
            purpose="requested authorization",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )
        other_authorization = app.external_access.authorize_explicit(
            purpose="different authorization",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )
        wrong_source = app.external_access.capture_url(
            other_authorization.authorization_id,
            "https://example.com/wrong-authorization",
        ).source.source_id

        job = app.research.enqueue_local_plus_web(
            query="this linkage must fail closed",
            authorization_id=authorization.authorization_id,
            captured_source_ids=(wrong_source,),
        )
        scope = app.research.initialize(job.job_id)

        with pytest.raises(ResearchSnapshotError, match="capture linkage"):
            app.research.repository.freeze_local_candidates(scope.scope_id)
    finally:
        app.stop()
