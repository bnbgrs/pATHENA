from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

import pytest

from athena.source.blob_store import SourceChangedDuringCaptureError
from athena.source.import_intake import (
    ImportIntakeService,
    ImportOrigin,
    ImportPreflightBlockedError,
    ImportRequest,
    ImportRequestError,
    ImportState,
    SymlinkPolicy,
)
from athena.storage.paths import RuntimePaths


class _FakeSources:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Path, uuid.UUID | None]] = []
        self.results: list[object | BaseException] = []

    def capture_file(self, path: Path) -> Any:
        self.calls.append(("plain", path, None))
        return self._next_result(path)

    def capture_protected_file(
        self,
        path: Path,
        *,
        protection_scope_id: uuid.UUID,
    ) -> Any:
        self.calls.append(("protected", path, protection_scope_id))
        return self._next_result(path)

    def _next_result(self, path: Path) -> object:
        if not self.results:
            return {"path": path}
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


def _runtime_paths(tmp_path: Path, *, archive: bool = True) -> RuntimePaths:
    local = tmp_path / "local"
    state = local / "state"
    spool = state / "spool"
    derived = local / "derived"
    logs = local / "logs"
    temp = local / "tmp"
    for path in (state, spool, derived, logs, temp):
        path.mkdir(parents=True, exist_ok=True)
    archive_root = tmp_path / "archive" if archive else None
    if archive_root is not None:
        archive_root.mkdir(parents=True)
    return RuntimePaths(
        local_root=local,
        state_root=state,
        database_path=state / "athena.db",
        spool_root=spool,
        derived_root=derived,
        log_root=logs,
        temp_root=temp,
        archive_root=archive_root,
        backup_root=None,
        projection_root=None,
    )


def _service(tmp_path: Path, *, archive: bool = True) -> tuple[ImportIntakeService, _FakeSources]:
    sources = _FakeSources()
    service = ImportIntakeService(  # type: ignore[arg-type]
        sources=sources,
        paths=_runtime_paths(tmp_path, archive=archive),
    )
    return service, sources


def test_request_round_trips_exact_json_payload(tmp_path: Path) -> None:
    scope_id = uuid.uuid4()
    request = ImportRequest.from_paths(
        [tmp_path / "a", tmp_path / "b"],
        origin=ImportOrigin.DRAG_DROP,
        recursive=False,
        symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
        max_file_bytes=123,
        expected_count=2,
        protection_scope_id=scope_id,
        include_system_metadata=True,
    )

    restored = ImportRequest.from_payload(request.to_payload())

    assert restored == request


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("recursive", 1),
        ("temporary", 0),
        ("do_not_store", "false"),
        ("include_system_metadata", None),
    ],
)
def test_request_rejects_non_bool_json_values(
    tmp_path: Path,
    field: str,
    bad_value: object,
) -> None:
    payload = ImportRequest.from_paths([tmp_path]).to_payload()
    payload[field] = bad_value

    with pytest.raises(ImportRequestError):
        ImportRequest.from_payload(payload)


def test_request_rejects_noncanonical_persisted_paths(tmp_path: Path) -> None:
    relative_payload = ImportRequest.from_paths([tmp_path]).to_payload()
    relative_payload["roots"] = ["relative/path"]
    with pytest.raises(ImportRequestError):
        ImportRequest.from_payload(relative_payload)

    normalized = os.path.normpath(os.path.abspath(os.fspath(tmp_path)))
    with pytest.raises(ImportRequestError):
        ImportRequest(roots=(normalized + os.sep + ".",))


def test_recursive_preflight_is_deterministic_and_reports_system_metadata(
    tmp_path: Path,
) -> None:
    root = tmp_path / "input"
    (root / "z").mkdir(parents=True)
    (root / "a.txt").write_text("a", encoding="utf-8")
    (root / "z" / "b.txt").write_text("b", encoding="utf-8")
    (root / ".DS_Store").write_text("meta", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("meta", encoding="utf-8")
    service, _sources = _service(tmp_path)

    preflight = service.preflight(
        ImportRequest.from_paths([root], origin=ImportOrigin.FOLDER)
    )

    assert [item.path.name for item in preflight.candidates] == ["a.txt", "b.txt"]
    assert preflight.total_bytes == 2
    assert not preflight.blocked
    filtered = [issue for issue in preflight.issues if issue.code == "filtered_system_metadata"]
    assert {issue.path.name for issue in filtered if issue.path is not None} == {".DS_Store", ".git"}


def test_non_recursive_folder_does_not_descend(tmp_path: Path) -> None:
    root = tmp_path / "input"
    nested = root / "nested"
    nested.mkdir(parents=True)
    (root / "top.txt").write_text("top", encoding="utf-8")
    (nested / "deep.txt").write_text("deep", encoding="utf-8")
    service, _sources = _service(tmp_path)

    preflight = service.preflight(
        ImportRequest.from_paths([root], recursive=False)
    )

    assert [item.path.name for item in preflight.candidates] == ["top.txt"]


def test_default_symlink_policy_does_not_follow(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    target = root / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = root / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    service, _sources = _service(tmp_path)

    preflight = service.preflight(ImportRequest.from_paths([root]))

    assert [item.path.name for item in preflight.candidates] == ["target.txt"]
    assert any(issue.code == "link_not_followed" for issue in preflight.issues)


def test_follow_policy_rejects_link_outside_selected_root(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret", encoding="utf-8")
    link = root / "outside-link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    service, _sources = _service(tmp_path)

    preflight = service.preflight(
        ImportRequest.from_paths(
            [root],
            symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
        )
    )

    assert preflight.blocked
    assert any(issue.code == "link_outside_selected_root" for issue in preflight.issues)
    assert not preflight.candidates


def test_follow_policy_detects_directory_cycle(tmp_path: Path) -> None:
    root = tmp_path / "input"
    child = root / "child"
    child.mkdir(parents=True)
    (child / "a.txt").write_text("a", encoding="utf-8")
    cycle = child / "back"
    try:
        cycle.symlink_to(root, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    service, _sources = _service(tmp_path)

    preflight = service.preflight(
        ImportRequest.from_paths(
            [root],
            symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
        )
    )

    assert preflight.blocked
    assert any(issue.code == "directory_cycle" for issue in preflight.issues)
    assert [item.path.name for item in preflight.candidates] == ["a.txt"]


def test_preflight_enforces_size_and_reports_expected_count(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    large = root / "large.bin"
    large.write_bytes(b"12345")
    service, _sources = _service(tmp_path)

    preflight = service.preflight(
        ImportRequest.from_paths(
            [root],
            max_file_bytes=4,
            expected_count=1,
        )
    )

    assert preflight.blocked
    assert any(issue.code == "max_file_size_exceeded" for issue in preflight.issues)
    assert any(issue.code == "expected_count_mismatch" for issue in preflight.issues)


@pytest.mark.parametrize("field", ["temporary", "do_not_store"])
def test_nonpersistent_policy_flags_fail_closed_before_capture(
    tmp_path: Path,
    field: str,
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("x", encoding="utf-8")
    service, sources = _service(tmp_path)
    kwargs = {field: True}
    request = ImportRequest.from_paths([source], **kwargs)  # type: ignore[arg-type]

    with pytest.raises(ImportPreflightBlockedError):
        service.capture(request)

    assert sources.calls == []


def test_offline_archive_is_warning_not_blocker(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("x", encoding="utf-8")
    paths = _runtime_paths(tmp_path)
    assert paths.archive_root is not None
    paths.archive_root.rmdir()
    sources = _FakeSources()
    service = ImportIntakeService(  # type: ignore[arg-type]
        sources=sources,
        paths=paths,
    )

    preflight = service.preflight(ImportRequest.from_paths([source]))

    assert not preflight.blocked
    assert not preflight.archive_available
    assert any(
        issue.code == "archive_root_unavailable_spool_will_be_used"
        for issue in preflight.issues
    )


def test_capture_retries_source_mutation_exactly_once(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("x", encoding="utf-8")
    service, sources = _service(tmp_path)
    sentinel = object()
    sources.results = [SourceChangedDuringCaptureError("changed"), sentinel]

    result = service.capture(ImportRequest.from_paths([source]))

    assert result.state is ImportState.READY
    assert result.captures == (sentinel,)
    assert len(sources.calls) == 2


def test_second_mutation_failure_is_sanitized_and_not_retried_forever(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("x", encoding="utf-8")
    service, sources = _service(tmp_path)
    sources.results = [
        SourceChangedDuringCaptureError("changed once"),
        RuntimeError("sensitive raw detail"),
    ]

    result = service.capture(ImportRequest.from_paths([source]))

    assert result.state is ImportState.FAILED
    assert result.failures[0].error_type == "RuntimeError"
    assert len(sources.calls) == 2


def test_mixed_capture_success_and_failure_returns_partial(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("a", encoding="utf-8")
    second.write_text("b", encoding="utf-8")
    service, sources = _service(tmp_path)
    sentinel = object()
    sources.results = [sentinel, RuntimeError("no")]

    result = service.capture(ImportRequest.from_paths([first, second]))

    assert result.state is ImportState.PARTIAL
    assert result.captures == (sentinel,)
    assert result.failures[0].path == second


def test_protected_capture_forwards_exact_scope(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("x", encoding="utf-8")
    service, sources = _service(tmp_path)
    scope_id = uuid.uuid4()

    result = service.capture(
        ImportRequest.from_paths(
            [source],
            protection_scope_id=scope_id,
        )
    )

    assert result.state is ImportState.READY
    assert sources.calls == [("protected", source, scope_id)]
