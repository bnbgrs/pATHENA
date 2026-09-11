from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

import athena.storage.database as database_module
from athena.storage.database import DatabaseNotStartedError, SQLiteDatabase
from athena.storage.recovery import (
    DatabaseRecoveryRequiredError,
    assert_database_preflight_current,
    inspect_database_read_only,
)


def _create_valid_database(path: Path) -> None:
    database = SQLiteDatabase(path)
    database.start()
    database.stop()


def _remove_sidecars(path: Path) -> None:
    for suffix in ("-wal", "-shm"):
        sidecar = path.with_name(f"{path.name}{suffix}")
        if sidecar.exists() or os.path.lexists(sidecar):
            sidecar.unlink()


def test_preflight_report_binds_primary_wal_and_shm_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "athena.db"
    _create_valid_database(path)

    report = inspect_database_read_only(path)

    assert report.file_set.primary.exists is True
    assert report.file_set.primary.path == path
    assert report.file_set.wal.exists == report.wal_present
    assert report.file_set.shm.exists == report.shm_present
    assert_database_preflight_current(report)


def test_writer_start_rejects_sidecar_mutation_after_preflight(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    _create_valid_database(path)
    _remove_sidecars(path)
    real_preflight = inspect_database_read_only
    injected = False

    def inspect_then_mutate(candidate: Path):
        nonlocal injected
        report = real_preflight(candidate)
        wal = candidate.with_name(f"{candidate.name}-wal")
        wal.write_bytes(b"post-preflight sidecar substitution")
        injected = True
        return report

    monkeypatch.setattr(database_module, "inspect_database_read_only", inspect_then_mutate)
    database = SQLiteDatabase(path)

    with pytest.raises(DatabaseRecoveryRequiredError, match="file set changed"):
        database.start()

    assert injected is True
    with pytest.raises(DatabaseNotStartedError):
        _ = database.connection


def test_writer_start_rejects_primary_replacement_during_connect(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    replacement = tmp_path / "replacement.db"
    _create_valid_database(path)
    _remove_sidecars(path)
    shutil.copy2(path, replacement)
    real_open_writer = database_module._open_writer_connection
    replaced = False

    def replacing_writer(candidate: Path, *, busy_timeout_ms: int):
        nonlocal replaced
        if not replaced:
            os.replace(replacement, candidate)
            replaced = True
        return real_open_writer(candidate, busy_timeout_ms=busy_timeout_ms)

    monkeypatch.setattr(database_module, "_open_writer_connection", replacing_writer)
    database = SQLiteDatabase(path)

    with pytest.raises(DatabaseRecoveryRequiredError, match="primary filesystem identity changed"):
        database.start()

    assert replaced is True
    with pytest.raises(DatabaseNotStartedError):
        _ = database.connection
