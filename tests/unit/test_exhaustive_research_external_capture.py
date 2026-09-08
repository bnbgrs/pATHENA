from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.external.gateway import ExternalResponse
from athena.source.models import SourceType


class _CountingExternalTransport:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def fetch(
        self,
        url: str,
        *,
        max_bytes: int,
        timeout_seconds: float,
    ) -> ExternalResponse:
        del max_bytes, timeout_seconds
        self.calls.append(url)
        return ExternalResponse(
            final_url=url,
            status=200,
            headers={"content-type": "text/plain; charset=utf-8"},
            body=b"captured external evidence for exhaustive research",
        )


def test_external_evidence_is_captured_and_pinned_before_research_use(
    tmp_path: Path,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start(run_startup_maintenance=False)
    try:
        transport = _CountingExternalTransport()
        app.external_access.transports["direct_explicit"] = transport
        authorization = app.external_access.authorize_explicit(
            purpose="exhaustive research external evidence",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )

        capture = app.external_access.capture_url(
            authorization.authorization_id,
            "https://example.com/research-evidence",
        )
        source = capture.source
        assert source.source_type is SourceType.WEB_SNAPSHOT
        assert transport.calls == ["https://example.com/research-evidence"]

        capture_row = app.database.connection.execute(
            """
            SELECT
                esc.authorization_id,
                esc.access_event_id,
                esc.provenance_url,
                e.source_id,
                e.outcome
            FROM external_source_captures AS esc
            JOIN external_access_events AS e
              ON e.event_id = esc.access_event_id
            WHERE esc.source_id = ?
            """,
            (source.source_id.bytes,),
        ).fetchone()
        assert capture_row is not None
        assert bytes(capture_row["authorization_id"]) == authorization.authorization_id.bytes
        assert bytes(capture_row["source_id"]) == source.source_id.bytes
        assert capture_row["outcome"] == "captured"
        assert "example.com/research-evidence" in str(capture_row["provenance_url"])

        snapshot_path = app.sources.verify(source.source_id)
        snapshot_bytes = snapshot_path.read_bytes()
        assert snapshot_bytes == b"captured external evidence for exhaustive research"

        job = app.research.enqueue_local_plus_web(
            query="Use the captured external evidence.",
            authorization_id=authorization.authorization_id,
            captured_source_ids=(source.source_id,),
        )
        scope = app.research.initialize(job.job_id)
        app.research.repository.freeze_local_candidates(scope.scope_id)
        candidates = app.research.repository.list_candidates(scope.scope_id)

        assert tuple(candidate.source_id for candidate in candidates) == (source.source_id,)
        pinned_source, pinned_blob = app.sources.get(candidates[0].source_id)
        assert pinned_source.source_id == source.source_id
        assert pinned_source.source_type is SourceType.WEB_SNAPSHOT
        assert pinned_source.content_sha256 == source.content_sha256
        assert pinned_blob.integrity_sha256 == source.content_sha256
        assert app.sources.verify(pinned_source.source_id).read_bytes() == snapshot_bytes

        assert transport.calls == ["https://example.com/research-evidence"]
    finally:
        app.stop()
