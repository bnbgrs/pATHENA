from __future__ import annotations

from pathlib import Path

from athena.storage.paths import RuntimePaths
from athena.storage.storage_runtime import build_storage_runtime


def _paths(tmp_path: Path) -> RuntimePaths:
    local = (tmp_path / "local").absolute()
    state = local / "state"
    return RuntimePaths(
        local_root=local,
        state_root=state,
        database_path=state / "athena.db",
        spool_root=state / "spool",
        derived_root=local / "derived",
        log_root=local / "logs",
        temp_root=local / "tmp",
        archive_root=None,
        backup_root=None,
        projection_root=None,
    )


def test_storage_runtime_shares_one_disk_pressure_authority(tmp_path: Path) -> None:
    paths = _paths(tmp_path)

    runtime = build_storage_runtime(paths)

    assert runtime.database.disk_pressure is runtime.disk_pressure
    assert runtime.bootstrap.disk_pressure is runtime.disk_pressure
    assert runtime.bootstrap.database is runtime.database
    assert runtime.database.path == paths.database_path
    assert runtime.bootstrap.paths is paths


def test_build_storage_runtime_has_no_filesystem_side_effects(tmp_path: Path) -> None:
    paths = _paths(tmp_path)

    _runtime = build_storage_runtime(paths)

    assert not paths.local_root.exists()
    assert not paths.database_path.exists()
