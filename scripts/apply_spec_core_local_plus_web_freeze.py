from __future__ import annotations

from pathlib import Path

REPOSITORY = Path("src/athena/research/repository.py")
TESTS = Path("tests/unit/test_research_local_plus_web.py")
WORKFLOW = Path(".github/workflows/spec-core-local-plus-web-freeze.yml")
SELF = Path(__file__)

old = '''            if scope.internet_scope_json is not None:\n                raise ResearchScopeUnsupportedError(\n                    "Foundation local discovery does not support internet_scope."\n                )\n            if scope.mode not in {\n                ResearchMode.LOCAL_EXHAUSTIVE,\n                ResearchMode.HISTORICAL_BACKFILL,\n            }:\n                raise ResearchScopeUnsupportedError(\n                    f"Foundation discovery does not support Research mode {scope.mode.value!r}."\n                )\n\n            source_types = _json_string_array(\n                scope.source_types_json,\n                "source_types_json",\n            )\n            explicit_source_ids = tuple(\n                uuid.UUID(value)\n                for value in _json_string_array(\n                    scope.explicit_source_ids_json,\n                    "explicit_source_ids_json",\n                )\n            )\n            rows = self._select_sources_as_of(\n                connection,\n                snapshot_commit_seq=scope.snapshot_commit_seq,\n                source_types=source_types,\n                explicit_source_ids=explicit_source_ids,\n                time_start_us=scope.time_start_us,\n                time_end_us=scope.time_end_us,\n            )\n'''

new = '''            internet_scope: Mapping[str, Any] | None = None\n            if scope.internet_scope_json is not None:\n                decoded_scope = json.loads(scope.internet_scope_json)\n                if not isinstance(decoded_scope, dict):\n                    raise ResearchScopeUnsupportedError(\n                        "Research internet_scope must be a canonical object."\n                    )\n                internet_scope = decoded_scope\n\n            if scope.mode not in {\n                ResearchMode.LOCAL_EXHAUSTIVE,\n                ResearchMode.HISTORICAL_BACKFILL,\n                ResearchMode.LOCAL_PLUS_WEB,\n            }:\n                raise ResearchScopeUnsupportedError(\n                    f"Foundation discovery does not support Research mode {scope.mode.value!r}."\n                )\n\n            authorized_external_source_ids: tuple[uuid.UUID, ...] = ()\n            all_external_source_ids: set[uuid.UUID] = set()\n            if scope.mode is ResearchMode.LOCAL_PLUS_WEB:\n                if internet_scope is None:\n                    raise ResearchScopeUnsupportedError(\n                        "Local+Web discovery requires explicit internet_scope provenance."\n                    )\n                authorization_raw = internet_scope.get("authorization_id")\n                captured_raw = internet_scope.get("captured_source_ids")\n                if not isinstance(authorization_raw, str):\n                    raise ResearchScopeUnsupportedError(\n                        "Local+Web internet_scope requires authorization_id UUID text."\n                    )\n                if not isinstance(captured_raw, list) or not captured_raw:\n                    raise ResearchScopeUnsupportedError(\n                        "Local+Web internet_scope requires captured_source_ids."\n                    )\n                if any(not isinstance(value, str) for value in captured_raw):\n                    raise ResearchScopeUnsupportedError(\n                        "Local+Web captured_source_ids must contain UUID text."\n                    )\n                try:\n                    authorization_id = uuid.UUID(authorization_raw)\n                    authorized_external_source_ids = tuple(\n                        uuid.UUID(value) for value in captured_raw\n                    )\n                except ValueError as exc:\n                    raise ResearchScopeUnsupportedError(\n                        "Local+Web internet_scope contains a malformed UUID."\n                    ) from exc\n                canonical_captured = tuple(\n                    sorted(set(authorized_external_source_ids), key=str)\n                )\n                if (\n                    str(authorization_id) != authorization_raw\n                    or canonical_captured != authorized_external_source_ids\n                    or [str(value) for value in canonical_captured] != captured_raw\n                ):\n                    raise ResearchScopeUnsupportedError(\n                        "Local+Web internet_scope is not canonical."\n                    )\n\n                linked_rows = connection.execute(\n                    """\n                    SELECT source_id\n                    FROM external_source_captures\n                    WHERE authorization_id = ?\n                    ORDER BY source_id\n                    """,\n                    (uuid_to_blob(authorization_id),),\n                ).fetchall()\n                linked_source_ids = tuple(\n                    sorted(\n                        {uuid_from_blob(bytes(row["source_id"])) for row in linked_rows},\n                        key=str,\n                    )\n                )\n                if linked_source_ids != authorized_external_source_ids:\n                    raise ResearchSnapshotError(\n                        "Local+Web capture linkage does not match the explicit authorization."\n                    )\n                external_rows = connection.execute(\n                    "SELECT DISTINCT source_id FROM external_source_captures"\n                ).fetchall()\n                all_external_source_ids = {\n                    uuid_from_blob(bytes(row["source_id"])) for row in external_rows\n                }\n            elif internet_scope is not None:\n                raise ResearchScopeUnsupportedError(\n                    "Foundation local discovery does not support internet_scope."\n                )\n\n            source_types = _json_string_array(\n                scope.source_types_json,\n                "source_types_json",\n            )\n            explicit_source_ids = tuple(\n                uuid.UUID(value)\n                for value in _json_string_array(\n                    scope.explicit_source_ids_json,\n                    "explicit_source_ids_json",\n                )\n            )\n            selection_explicit_source_ids = (\n                ()\n                if scope.mode is ResearchMode.LOCAL_PLUS_WEB\n                else explicit_source_ids\n            )\n            rows = self._select_sources_as_of(\n                connection,\n                snapshot_commit_seq=scope.snapshot_commit_seq,\n                source_types=source_types,\n                explicit_source_ids=selection_explicit_source_ids,\n                time_start_us=scope.time_start_us,\n                time_end_us=scope.time_end_us,\n            )\n            if scope.mode is ResearchMode.LOCAL_PLUS_WEB:\n                authorized = set(authorized_external_source_ids)\n                rows = [\n                    row\n                    for row in rows\n                    if (\n                        uuid_from_blob(bytes(row["source_id"]))\n                        not in all_external_source_ids\n                        or uuid_from_blob(bytes(row["source_id"])) in authorized\n                    )\n                ]\n'''

text = REPOSITORY.read_text(encoding="utf-8")
if text.count(old) != 1:
    raise SystemExit("repository freeze anchor did not match exactly once")
REPOSITORY.write_text(text.replace(old, new), encoding="utf-8")

imports_old = '''from athena.config.settings import AthenaSettings\nfrom athena.core.application import AthenaApplication\nfrom athena.research.service import ResearchConfigurationError\n'''
imports_new = '''from athena.config.settings import AthenaSettings\nfrom athena.core.application import AthenaApplication\nfrom athena.external.gateway import ExternalResponse\nfrom athena.research.errors import ResearchSnapshotError\nfrom athena.research.service import ResearchConfigurationError\n'''

test_text = TESTS.read_text(encoding="utf-8")
if test_text.count(imports_old) != 1:
    raise SystemExit("test import anchor did not match exactly once")
test_text = test_text.replace(imports_old, imports_new)
append = r'''

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
'''
if "test_local_plus_web_freeze_unions_pinned_local_with_only_authorized_capture" in test_text:
    raise SystemExit("candidate freeze acceptance already present")
TESTS.write_text(test_text.rstrip() + append + "\n", encoding="utf-8")

SELF.unlink()
WORKFLOW.unlink(missing_ok=True)
