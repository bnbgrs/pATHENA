from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.paths import RuntimePaths


def _paths(tmp_path: Path) -> RuntimePaths:
    state = tmp_path / "state"
    return RuntimePaths(
        local_root=tmp_path,
        state_root=state,
        database_path=state / "athena.db",
        spool_root=state / "spool",
        derived_root=tmp_path / "derived",
        log_root=tmp_path / "logs",
        temp_root=tmp_path / "tmp",
        archive_root=None,
        backup_root=None,
        projection_root=None,
    )


def test_runtime_paths_accept_path_values(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    assert paths.required_local_directories[0] == tmp_path


def test_runtime_paths_reject_non_path_required_field(tmp_path: Path) -> None:
    state = tmp_path / "state"
    with pytest.raises(TypeError, match="database_path"):
        RuntimePaths(
            local_root=tmp_path,
            state_root=state,
            database_path="athena.db",  # type: ignore[arg-type]
            spool_root=state / "spool",
            derived_root=tmp_path / "derived",
            log_root=tmp_path / "logs",
            temp_root=tmp_path / "tmp",
            archive_root=None,
            backup_root=None,
            projection_root=None,
        )


def test_runtime_paths_reject_non_path_optional_field(tmp_path: Path) -> None:
    state = tmp_path / "state"
    with pytest.raises(TypeError, match="archive_root"):
        RuntimePaths(
            local_root=tmp_path,
            state_root=state,
            database_path=state / "athena.db",
            spool_root=state / "spool",
            derived_root=tmp_path / "derived",
            log_root=tmp_path / "logs",
            temp_root=tmp_path / "tmp",
            archive_root="archive",  # type: ignore[arg-type]
            backup_root=None,
            projection_root=None,
        )
