from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

from athena.storage.migration_clone import MigrationCloneError, create_migration_clone


def _create_source(path: Path, *, schema_version: int = 7) -> None:
    connection = sqlite3.connect(path, autocommit=True)
    try:
        connection.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("INSERT INTO items (value) VALUES ('alpha')")
        connection.execute(f"PRAGMA user_version = {schema_version}")
    finally:
        connection.close()


def test_migration_clone_uses_independent_sqlite_snapshot(tmp_path: Path) -> None:
    source = (tmp_path / "athena.db").absolute()
    candidate = (tmp_path / "athena.migrating.db").absolute()
    _create_source(source, schema_version=7)

    report = create_migration_clone(source_db=source, candidate_db=candidate)

    assert report.source_db == source
    assert report.candidate_db == candidate
    assert report.schema_version == 7
    assert report.database_size_bytes == candidate.stat().st_size
    assert report.database_size_bytes > 0

    clone = sqlite3.connect(candidate, autocommit=True)
    try:
        assert clone.execute("SELECT value FROM items").fetchall() == [("alpha",)]
    finally:
        clone.close()

    source_connection = sqlite3.connect(source, autocommit=True)
    try:
        source_connection.execute("INSERT INTO items (value) VALUES ('beta')")
    finally:
        source_connection.close()

    clone = sqlite3.connect(candidate, autocommit=True)
    try:
        assert clone.execute("SELECT value FROM items ORDER BY id").fetchall() == [
            ("alpha",)
        ]
    finally:
        clone.close()

    if os.name == "posix":
        assert candidate.stat().st_mode & 0o077 == 0


def test_migration_clone_refuses_existing_candidate(tmp_path: Path) -> None:
    source = (tmp_path / "athena.db").absolute()
    candidate = (tmp_path / "athena.migrating.db").absolute()
    _create_source(source)
    candidate.write_bytes(b"preserve-me")

    with pytest.raises(MigrationCloneError, match="must not already exist"):
        create_migration_clone(source_db=source, candidate_db=candidate)

    assert candidate.read_bytes() == b"preserve-me"


def test_migration_clone_refuses_stale_candidate_sidecar(tmp_path: Path) -> None:
    source = (tmp_path / "athena.db").absolute()
    candidate = (tmp_path / "athena.migrating.db").absolute()
    _create_source(source)
    sidecar = candidate.with_name(f"{candidate.name}-wal")
    sidecar.write_bytes(b"stale")

    with pytest.raises(MigrationCloneError, match="stale SQLite sidecars"):
        create_migration_clone(source_db=source, candidate_db=candidate)

    assert sidecar.read_bytes() == b"stale"
    assert not candidate.exists()


def test_migration_clone_rejects_foreign_key_corruption_and_cleans_candidate(
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    candidate = (tmp_path / "athena.migrating.db").absolute()
    connection = sqlite3.connect(source, autocommit=True)
    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
        connection.execute(
            "CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))"
        )
        connection.execute("INSERT INTO child (parent_id) VALUES (999)")
        connection.execute("PRAGMA user_version = 4")
    finally:
        connection.close()

    with pytest.raises(MigrationCloneError, match="foreign_key_check"):
        create_migration_clone(source_db=source, candidate_db=candidate)

    assert not candidate.exists()
    assert not candidate.with_name(f"{candidate.name}-wal").exists()
    assert not candidate.with_name(f"{candidate.name}-shm").exists()


def test_migration_clone_refuses_symlink_candidate_parent(tmp_path: Path) -> None:
    source = (tmp_path / "athena.db").absolute()
    _create_source(source)
    real_parent = tmp_path / "migration"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked-migration"
    try:
        linked_parent.symlink_to(real_parent, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")

    candidate = (linked_parent / "athena.migrating.db").absolute()

    with pytest.raises(MigrationCloneError, match="symbolic link"):
        create_migration_clone(source_db=source, candidate_db=candidate)

    assert not (real_parent / "athena.migrating.db").exists()


def test_migration_clone_refuses_same_source_and_candidate(tmp_path: Path) -> None:
    source = (tmp_path / "athena.db").absolute()
    _create_source(source)

    with pytest.raises(MigrationCloneError, match="must differ"):
        create_migration_clone(source_db=source, candidate_db=source)
