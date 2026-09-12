from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest

import athena.storage.database as database_module
from athena.storage.database import SQLiteDatabase
from athena.storage.recovery import (
    DatabasePreflightReport,
    DatabaseStartupIdentityChangedError,
    assert_database_file_set_identity,
    capture_database_file_set_identity,
    inspect_database_read_only,
)


def _create_current_database(path: Path) -> None:
    database = SQLiteDatabase(path)
    database.start()
    database.stop()


def _inspect_without_sidecars(path: Path) -> DatabasePreflightReport:
    validated = inspect_database_read_only(path)
    checkpoint = sqlite3.connect(path, autocommit=True)
    try:
        checkpoint.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    finally:
        checkpoint.close()
    for suffix in ("-wal", "-shm"):
        path.with_name(f"{path.name}{suffix}").unlink(missing_ok=True)

    identity = capture_database_file_set_identity(path)
    assert identity.database.exists
    assert not identity.wal.exists
    assert not identity.shm.exists
    return DatabasePreflightReport(
        path=validated.path,
        exists=True,
        application_id=validated.application_id,
        schema_version=validated.schema_version,
        wal_present=False,
        shm_present=False,
        file_set_identity=identity,
    )


def test_file_set_identity_detects_each_member_replacement(tmp_path: Path) -> None:
    database_path = tmp_path / "athena.db"
    wal_path = tmp_path / "athena.db-wal"
    shm_path = tmp_path / "athena.db-shm"
    for path in (database_path, wal_path, shm_path):
        path.write_bytes(path.name.encode("utf-8"))

    for target in (database_path, wal_path, shm_path):
        expected = capture_database_file_set_identity(database_path)
        replacement = tmp_path / f"{target.name}.replacement"
        replacement.write_bytes(b"replacement")
        os.replace(replacement, target)

        with pytest.raises(DatabaseStartupIdentityChangedError, match="identity changed"):
            assert_database_file_set_identity(database_path, expected)


def test_bound_preflight_rejects_primary_substitution_during_writer_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "athena.db"
    replacement_path = tmp_path / "replacement.db"
    _create_current_database(database_path)
    _create_current_database(replacement_path)

    preflight = inspect_database_read_only(database_path)
    original_identity = preflight.file_set_identity
    assert original_identity is not None

    database = SQLiteDatabase(database_path)
    database.bind_startup_preflight(preflight)
    real_connect = sqlite3.connect
    replacement_identity = capture_database_file_set_identity(replacement_path).database

    def racing_connect(*args: Any, **kwargs: Any) -> sqlite3.Connection:
        os.replace(replacement_path, database_path)
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(database_module.sqlite3, "connect", racing_connect)

    with pytest.raises(DatabaseStartupIdentityChangedError, match="identity changed"):
        database.start()

    current_identity = capture_database_file_set_identity(database_path).database
    assert current_identity == replacement_identity
    assert current_identity != original_identity.database


def test_bound_missing_preflight_rejects_file_created_before_writer_start(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "athena.db"
    preflight = inspect_database_read_only(database_path)
    assert preflight.exists is False

    database = SQLiteDatabase(database_path)
    database.bind_startup_preflight(preflight)

    database_path.write_bytes(b"foreign")

    with pytest.raises(DatabaseStartupIdentityChangedError, match="identity changed"):
        database.start()

    assert database_path.read_bytes() == b"foreign"


def test_bound_preflight_rejects_sidecar_mutation_before_writer_open(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "athena.db"
    _create_current_database(database_path)
    preflight = inspect_database_read_only(database_path)
    file_set_identity = preflight.file_set_identity
    assert file_set_identity is not None

    sidecars = (
        (
            database_path.with_name(f"{database_path.name}-wal"),
            file_set_identity.wal,
        ),
        (
            database_path.with_name(f"{database_path.name}-shm"),
            file_set_identity.shm,
        ),
    )
    target, target_identity = sidecars[0]
    foreign_bytes = b"foreign-sidecar"
    if target_identity.exists:
        replacement = tmp_path / f"{target.name}.replacement"
        replacement.write_bytes(foreign_bytes)
        os.replace(replacement, target)
    else:
        target.write_bytes(foreign_bytes)

    database = SQLiteDatabase(database_path)
    database.bind_startup_preflight(preflight)

    with pytest.raises(DatabaseStartupIdentityChangedError, match="identity changed"):
        database.start()

    assert target.read_bytes() == foreign_bytes


def test_bound_preflight_rejects_partial_sidecar_publication(tmp_path: Path) -> None:
    database_path = tmp_path / "athena.db"
    _create_current_database(database_path)
    preflight = _inspect_without_sidecars(database_path)
    wal_path = database_path.with_name(f"{database_path.name}-wal")
    wal_path.write_bytes(b"foreign-sidecar")

    database = SQLiteDatabase(database_path)
    database.bind_startup_preflight(preflight)

    with pytest.raises(DatabaseStartupIdentityChangedError, match="identity changed"):
        database.start()

    assert wal_path.read_bytes() == b"foreign-sidecar"


def test_bound_preflight_accepts_valid_concurrent_sidecar_publication(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "athena.db"
    _create_current_database(database_path)
    preflight = _inspect_without_sidecars(database_path)
    original_identity = preflight.file_set_identity
    assert original_identity is not None

    concurrent = sqlite3.connect(database_path, autocommit=True)
    try:
        concurrent.execute("BEGIN IMMEDIATE")
        published_identity = capture_database_file_set_identity(database_path)
        assert published_identity.database == original_identity.database
        assert published_identity.wal.exists
        assert published_identity.shm.exists

        database = SQLiteDatabase(database_path)
        database.bind_startup_preflight(preflight)
        database.start()
        database.stop()
    finally:
        if concurrent.in_transaction:
            concurrent.execute("ROLLBACK")
        concurrent.close()
