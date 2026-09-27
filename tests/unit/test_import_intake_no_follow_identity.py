from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from athena.source.import_intake import ImportIntakeService, ImportRequest, SymlinkPolicy
from athena.source.service import SourceCaptureService
from athena.storage.paths import RuntimePaths


class _UnusedSources:
    pass


def _paths(tmp_path: Path) -> RuntimePaths:
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


def _service(tmp_path: Path) -> ImportIntakeService:
    return ImportIntakeService(
        sources=cast(SourceCaptureService, _UnusedSources()),
        paths=_paths(tmp_path),
    )


def _symlink(path: Path, target: Path) -> None:
    path.unlink()
    try:
        path.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")


def test_selected_file_swap_to_symlink_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = tmp_path / "selected.txt"
    outside = tmp_path / "outside.txt"
    selected.write_text("safe", encoding="utf-8")
    outside.write_text("outside", encoding="utf-8")
    service = _service(tmp_path)
    original = Path.resolve
    swapped = False

    def racing_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        nonlocal swapped
        if self == selected and not swapped:
            swapped = True
            _symlink(selected, outside)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", racing_resolve)
    preflight = service.preflight(
        ImportRequest.from_paths(
            [selected],
            symlink_policy=SymlinkPolicy.DO_NOT_FOLLOW,
        )
    )
    assert preflight.blocked
    assert preflight.candidates == ()
    assert any(
        issue.code == "link_introduced_during_preflight" and issue.blocking
        for issue in preflight.issues
    )


def test_directory_entry_swap_to_symlink_is_not_followed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "input"
    root.mkdir()
    entry = root / "entry.txt"
    target = root / "target.txt"
    entry.write_text("safe", encoding="utf-8")
    target.write_text("target", encoding="utf-8")
    service = _service(tmp_path)
    original = Path.resolve
    swapped = False

    def racing_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        nonlocal swapped
        if self == entry and not swapped:
            swapped = True
            _symlink(entry, target)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", racing_resolve)
    preflight = service.preflight(
        ImportRequest.from_paths(
            [root],
            symlink_policy=SymlinkPolicy.DO_NOT_FOLLOW,
        )
    )
    assert preflight.blocked
    assert all(candidate.path != entry for candidate in preflight.candidates)
    assert any(i.code == "link_introduced_during_preflight" and i.blocking for i in preflight.issues)


def test_stable_no_follow_file_remains_importable(tmp_path: Path) -> None:
    selected = tmp_path / "stable.txt"
    selected.write_text("stable", encoding="utf-8")
    service = _service(tmp_path)
    preflight = service.preflight(
        ImportRequest.from_paths(
            [selected],
            symlink_policy=SymlinkPolicy.DO_NOT_FOLLOW,
        )
    )
    assert not preflight.blocked
    assert len(preflight.candidates) == 1
    assert preflight.candidates[0].capture_path == selected.resolve()
