from __future__ import annotations

from pathlib import Path
from typing import cast

from athena.source.import_intake import ImportIntakeService, ImportRequest
from athena.source.service import SourceCaptureService
from athena.storage.paths import RuntimePaths


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


def _service(tmp_path: Path) -> ImportIntakeService:
    return ImportIntakeService(
        sources=cast(SourceCaptureService, object()),
        paths=_runtime_paths(tmp_path),
    )


def test_selected_system_metadata_directory_is_filtered_at_root(tmp_path: Path) -> None:
    root = tmp_path / ".git"
    root.mkdir()
    (root / "config").write_text("private repository metadata", encoding="utf-8")

    preflight = _service(tmp_path).preflight(ImportRequest.from_paths([root]))

    assert preflight.blocked
    assert not preflight.candidates
    assert any(
        issue.code == "filtered_system_metadata" and issue.path == root
        for issue in preflight.issues
    )
    assert any(issue.code == "no_importable_files" for issue in preflight.issues)


def test_filtered_metadata_root_does_not_block_other_selected_file(tmp_path: Path) -> None:
    metadata_root = tmp_path / ".git"
    metadata_root.mkdir()
    (metadata_root / "config").write_text("private metadata", encoding="utf-8")
    selected_file = tmp_path / "notes.txt"
    selected_file.write_text("keep", encoding="utf-8")

    preflight = _service(tmp_path).preflight(
        ImportRequest.from_paths([metadata_root, selected_file])
    )

    assert not preflight.blocked
    assert [candidate.path for candidate in preflight.candidates] == [selected_file]
    assert any(
        issue.code == "filtered_system_metadata" and issue.path == metadata_root
        for issue in preflight.issues
    )
    assert not any(issue.code == "no_importable_files" for issue in preflight.issues)


def test_selected_system_metadata_directory_can_be_explicitly_included(
    tmp_path: Path,
) -> None:
    root = tmp_path / ".git"
    root.mkdir()
    config = root / "config"
    config.write_text("explicit metadata", encoding="utf-8")

    preflight = _service(tmp_path).preflight(
        ImportRequest.from_paths([root], include_system_metadata=True)
    )

    assert not preflight.blocked
    assert [candidate.path for candidate in preflight.candidates] == [config]
    assert not any(
        issue.code == "filtered_system_metadata" for issue in preflight.issues
    )
