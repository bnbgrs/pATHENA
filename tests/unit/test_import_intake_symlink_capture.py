from __future__ import annotations

import uuid
from pathlib import Path
from typing import cast

import pytest

from athena.source.import_intake import (
    ImportIntakeService,
    ImportRequest,
    ImportState,
    SymlinkPolicy,
)
from athena.source.service import SourceCaptureService
from athena.storage.paths import RuntimePaths


class _RecordingSources:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Path, uuid.UUID | None]] = []

    def capture_file(self, path: Path) -> object:
        self.calls.append(("plain", path, None))
        return object()

    def capture_protected_file(
        self,
        path: Path,
        *,
        protection_scope_id: uuid.UUID,
    ) -> object:
        self.calls.append(("protected", path, protection_scope_id))
        return object()


def _runtime_paths(tmp_path: Path) -> RuntimePaths:
    local = tmp_path / "local"
    state = local / "state"
    spool = state / "spool"
    derived = local / "derived"
    logs = local / "logs"
    temp = local / "tmp"
    archive = tmp_path / "archive"
    for path in (state, spool, derived, logs, temp, archive):
        path.mkdir(parents=True, exist_ok=True)
    return RuntimePaths(
        local_root=local,
        state_root=state,
        database_path=state / "athena.db",
        spool_root=spool,
        derived_root=derived,
        log_root=logs,
        temp_root=temp,
        archive_root=archive,
        backup_root=None,
        projection_root=None,
    )


def _service(
    tmp_path: Path,
) -> tuple[ImportIntakeService, _RecordingSources]:
    sources = _RecordingSources()
    service = ImportIntakeService(
        sources=cast(SourceCaptureService, sources),
        paths=_runtime_paths(tmp_path),
    )
    return service, sources


def _file_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")


def _directory_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation is unavailable in this environment")


def test_followed_file_link_captures_validated_regular_target(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    target = root / "z-target.txt"
    target.write_text("grounded", encoding="utf-8")
    link = root / "a-link.txt"
    _file_symlink(link, target)
    service, sources = _service(tmp_path)

    request = ImportRequest.from_paths(
        [root],
        symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
    )
    preflight = service.preflight(request)

    assert not preflight.blocked
    assert len(preflight.candidates) == 1
    candidate = preflight.candidates[0]
    assert candidate.path == link
    assert candidate.capture_path == target.resolve()
    assert candidate.boundary == root.resolve()

    result = service.capture(request)

    assert result.state is ImportState.READY
    assert sources.calls == [("plain", target.resolve(), None)]
    assert not sources.calls[0][1].is_symlink()


def test_protected_followed_file_link_forwards_target_and_scope(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    target = root / "z-target.txt"
    target.write_text("protected", encoding="utf-8")
    link = root / "a-link.txt"
    _file_symlink(link, target)
    service, sources = _service(tmp_path)
    scope_id = uuid.uuid4()

    result = service.capture(
        ImportRequest.from_paths(
            [root],
            symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
            protection_scope_id=scope_id,
        )
    )

    assert result.state is ImportState.READY
    assert sources.calls == [("protected", target.resolve(), scope_id)]


def test_followed_directory_alias_is_duplicate_not_cycle(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    target_dir = root / "z-target-dir"
    target_dir.mkdir()
    target_file = target_dir / "inside.txt"
    target_file.write_text("inside", encoding="utf-8")
    alias = root / "a-link-dir"
    _directory_symlink(alias, target_dir)
    service, sources = _service(tmp_path)

    request = ImportRequest.from_paths(
        [root],
        symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
    )
    preflight = service.preflight(request)

    assert not preflight.blocked
    assert len(preflight.candidates) == 1
    candidate = preflight.candidates[0]
    assert candidate.path == alias / "inside.txt"
    assert candidate.capture_path == target_file.resolve()
    assert any(
        issue.code == "duplicate_directory_target" and not issue.blocking
        for issue in preflight.issues
    )
    assert not any(issue.code == "directory_cycle" for issue in preflight.issues)

    result = service.capture(request)

    assert result.state is ImportState.READY
    assert sources.calls == [("plain", target_file.resolve(), None)]


def test_followed_file_link_target_swap_fails_before_source_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "input"
    root.mkdir()
    targets = root / "targets"
    targets.mkdir()
    first = targets / "first.txt"
    second = targets / "second.txt"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")
    link = root / "a-link.txt"
    _file_symlink(link, first)
    service, sources = _service(tmp_path)
    request = ImportRequest.from_paths(
        [root],
        symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
        recursive=False,
    )
    preflight = service.preflight(request)
    assert not preflight.blocked
    assert len(preflight.candidates) == 1
    assert preflight.candidates[0].capture_path == first.resolve()

    link.unlink()
    _file_symlink(link, second)
    monkeypatch.setattr(service, "preflight", lambda _request: preflight)

    result = service.capture(request)

    assert result.state is ImportState.FAILED
    assert result.failures[0].path == link
    assert result.failures[0].error_type == "SourceChangedDuringCaptureError"
    assert sources.calls == []


def test_real_directory_cycle_remains_blocking(tmp_path: Path) -> None:
    root = tmp_path / "input"
    child = root / "child"
    child.mkdir(parents=True)
    (child / "item.txt").write_text("item", encoding="utf-8")
    back = child / "back"
    _directory_symlink(back, root)
    service, _sources = _service(tmp_path)

    preflight = service.preflight(
        ImportRequest.from_paths(
            [root],
            symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
        )
    )

    assert preflight.blocked
    assert any(
        issue.code == "directory_cycle" and issue.blocking
        for issue in preflight.issues
    )
