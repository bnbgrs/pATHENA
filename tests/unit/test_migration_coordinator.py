from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import athena.storage.migration_coordinator as migration_coordinator_module
from athena.storage.migration_coordinator import (
    MigrationCoordinatorError,
    run_clone_migration,
)
from athena.storage.migration_journal import (
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
)
from athena.storage.migration_safety import MigrationDescriptor


def _source(path: Path, *, version: int = 1) -> None:
    connection = sqlite3.connect(path, autocommit=True)
    try:
        connection.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("INSERT INTO items (value) VALUES ('old')")
        connection.execute(f"PRAGMA user_version = {version}")
    finally:
        connection.close()


def _descriptor(*, from_version: int = 1, to_version: int = 2) -> MigrationDescriptor:
    return MigrationDescriptor(
        migration_id=f"schema-v{from_version}-to-v{to_version}",
        from_version=from_version,
        to_version=to_version,
        reversible=False,
        requires_clone=True,
        estimated_space_factor=1.25,
        requires_rebuild=False,
    )


def _successful_executor(path: Path) -> None:
    connection = sqlite3.connect(path, autocommit=True)
    try:
        connection.execute("ALTER TABLE items ADD COLUMN migrated INTEGER NOT NULL DEFAULT 1")
        connection.execute("PRAGMA user_version = 2")
    finally:
        connection.close()


def test_clone_migration_completes_with_rollback_and_activated_journal(
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source)

    result = run_clone_migration(
        source_db=source,
        migration_root=root,
        descriptor=_descriptor(),
        emergency_reserve_bytes=0,
        started_at_us=123,
        executor=_successful_executor,
        available_bytes=10**12,
    )

    assert result.final_journal.phase is MigrationPhase.ACTIVATED
    assert result.final_journal.last_completed_step == "activation_complete"
    assert result.activation.active_db == source
    assert result.activation.rollback_db == root / "rollback.db"
    assert not (root / "candidate.db").exists()

    active = sqlite3.connect(source, autocommit=True)
    try:
        assert active.execute("PRAGMA user_version").fetchone() == (2,)
        assert active.execute("SELECT value, migrated FROM items").fetchall() == [
            ("old", 1)
        ]
    finally:
        active.close()

    rollback = sqlite3.connect(root / "rollback.db", autocommit=True)
    try:
        assert rollback.execute("PRAGMA user_version").fetchone() == (1,)
        assert rollback.execute("SELECT value FROM items").fetchall() == [("old",)]
    finally:
        rollback.close()

    persisted = MigrationJournalStore(root / "migration_state.json").load()
    assert persisted == result.final_journal


def test_clone_migration_blocks_before_journal_when_space_is_insufficient(
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source)
    called = False

    def executor(_path: Path) -> None:
        nonlocal called
        called = True

    with pytest.raises(MigrationCoordinatorError, match="Insufficient free space"):
        run_clone_migration(
            source_db=source,
            migration_root=root,
            descriptor=_descriptor(),
            emergency_reserve_bytes=0,
            started_at_us=123,
            executor=executor,
            available_bytes=0,
        )

    assert called is False
    assert not (root / "migration_state.json").exists()
    assert not (root / "candidate.db").exists()
    assert source.exists()


def test_clone_migration_refuses_existing_journal_without_overwriting(
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source)
    candidate = (root / "candidate.db").absolute()
    previous = MigrationJournalState(
        migration_id="previous",
        phase=MigrationPhase.MIGRATING,
        source_db=source,
        candidate_db=candidate,
        started_at_us=1,
        last_completed_step="clone_complete",
    )
    store = MigrationJournalStore(root / "migration_state.json")
    store.publish(previous)
    before = (root / "migration_state.json").read_bytes()

    with pytest.raises(MigrationCoordinatorError, match="Existing migration journal"):
        run_clone_migration(
            source_db=source,
            migration_root=root,
            descriptor=_descriptor(),
            emergency_reserve_bytes=0,
            started_at_us=123,
            executor=_successful_executor,
            available_bytes=10**12,
        )

    assert (root / "migration_state.json").read_bytes() == before
    assert source.exists()
    assert not candidate.exists()


def test_executor_failure_leaves_migrating_journal_and_original_active(
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source)

    def fail_executor(_path: Path) -> None:
        raise RuntimeError("simulated migration failure")

    with pytest.raises(RuntimeError, match="simulated migration failure"):
        run_clone_migration(
            source_db=source,
            migration_root=root,
            descriptor=_descriptor(),
            emergency_reserve_bytes=0,
            started_at_us=123,
            executor=fail_executor,
            available_bytes=10**12,
        )

    journal = MigrationJournalStore(root / "migration_state.json").load()
    assert journal is not None
    assert journal.phase is MigrationPhase.MIGRATING
    assert journal.last_completed_step == "clone_complete"
    assert source.exists()
    assert (root / "candidate.db").exists()
    assert not (root / "rollback.db").exists()


def test_source_version_mismatch_stops_before_executor(tmp_path: Path) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source, version=3)
    called = False

    def executor(_path: Path) -> None:
        nonlocal called
        called = True

    with pytest.raises(MigrationCoordinatorError, match="source version"):
        run_clone_migration(
            source_db=source,
            migration_root=root,
            descriptor=_descriptor(from_version=1, to_version=2),
            emergency_reserve_bytes=0,
            started_at_us=123,
            executor=executor,
            available_bytes=10**12,
        )

    assert called is False
    journal = MigrationJournalStore(root / "migration_state.json").load()
    assert journal is not None
    assert journal.phase is MigrationPhase.CLONING
    assert source.exists()
    assert (root / "candidate.db").exists()


def test_verification_failure_leaves_verifying_journal_and_original_active(
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source)

    def corrupt_executor(path: Path) -> None:
        connection = sqlite3.connect(path, autocommit=True)
        try:
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))"
            )
            connection.execute("INSERT INTO child (parent_id) VALUES (999)")
            connection.execute("PRAGMA user_version = 2")
        finally:
            connection.close()

    with pytest.raises(MigrationCoordinatorError, match="foreign_key_check"):
        run_clone_migration(
            source_db=source,
            migration_root=root,
            descriptor=_descriptor(),
            emergency_reserve_bytes=0,
            started_at_us=123,
            executor=corrupt_executor,
            available_bytes=10**12,
        )

    journal = MigrationJournalStore(root / "migration_state.json").load()
    assert journal is not None
    assert journal.phase is MigrationPhase.VERIFYING
    assert source.exists()
    assert (root / "candidate.db").exists()
    assert not (root / "rollback.db").exists()


def test_reparse_root_is_rejected_before_disk_or_sqlite_access(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    _source(source)
    original = migration_coordinator_module.is_link_boundary

    def simulate_reparse(path: Path) -> bool:
        return path == root or original(path)

    disk_accessed = False

    def fail_disk_usage(_path: Path) -> object:
        nonlocal disk_accessed
        disk_accessed = True
        raise AssertionError("disk usage must not cross a reparse boundary")

    monkeypatch.setattr(migration_coordinator_module, "is_link_boundary", simulate_reparse)
    monkeypatch.setattr(migration_coordinator_module.shutil, "disk_usage", fail_disk_usage)

    with pytest.raises(MigrationCoordinatorError, match="reparse-point boundary"):
        run_clone_migration(
            source_db=source,
            migration_root=root,
            descriptor=_descriptor(),
            emergency_reserve_bytes=0,
            started_at_us=123,
            executor=_successful_executor,
        )

    assert disk_accessed is False
    assert not (root / "migration_state.json").exists()
