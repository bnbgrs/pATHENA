from __future__ import annotations

from pathlib import Path

import pytest

import athena.storage.migration_activation as migration_activation_module
from athena.storage.migration_activation import (
    MigrationActivationError,
    activate_migration_candidate,
)


def _write(path: Path, value: bytes) -> None:
    path.write_bytes(value)


def test_activation_preserves_old_database_as_rollback(tmp_path: Path) -> None:
    migration_root = tmp_path / "migration"
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = (migration_root / "candidate.db").absolute()
    rollback = (migration_root / "rollback.db").absolute()
    _write(source, b"old-database")
    _write(candidate, b"new-database")

    report = activate_migration_candidate(
        source_db=source,
        candidate_db=candidate,
        rollback_db=rollback,
    )

    assert report.active_db == source
    assert report.rollback_db == rollback
    assert source.read_bytes() == b"new-database"
    assert rollback.read_bytes() == b"old-database"
    assert not candidate.exists()


def test_activation_refuses_source_wal_without_moving_files(tmp_path: Path) -> None:
    migration_root = tmp_path / "migration"
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = (migration_root / "candidate.db").absolute()
    rollback = (migration_root / "rollback.db").absolute()
    _write(source, b"old")
    _write(candidate, b"new")
    source.with_name(f"{source.name}-wal").write_bytes(b"wal")

    with pytest.raises(MigrationActivationError, match="WAL/SHM sidecar"):
        activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

    assert source.read_bytes() == b"old"
    assert candidate.read_bytes() == b"new"
    assert not rollback.exists()


def test_activation_refuses_candidate_sidecar_without_moving_files(tmp_path: Path) -> None:
    migration_root = tmp_path / "migration"
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = (migration_root / "candidate.db").absolute()
    rollback = (migration_root / "rollback.db").absolute()
    _write(source, b"old")
    _write(candidate, b"new")
    candidate.with_name(f"{candidate.name}-shm").write_bytes(b"shm")

    with pytest.raises(MigrationActivationError, match="WAL/SHM sidecar"):
        activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

    assert source.read_bytes() == b"old"
    assert candidate.read_bytes() == b"new"
    assert not rollback.exists()


def test_activation_refuses_existing_rollback_target(tmp_path: Path) -> None:
    migration_root = tmp_path / "migration"
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = (migration_root / "candidate.db").absolute()
    rollback = (migration_root / "rollback.db").absolute()
    _write(source, b"old")
    _write(candidate, b"new")
    _write(rollback, b"existing")

    with pytest.raises(MigrationActivationError, match="must not already exist"):
        activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

    assert source.read_bytes() == b"old"
    assert candidate.read_bytes() == b"new"
    assert rollback.read_bytes() == b"existing"


def test_activation_restores_original_if_candidate_move_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    migration_root = tmp_path / "migration"
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = (migration_root / "candidate.db").absolute()
    rollback = (migration_root / "rollback.db").absolute()
    _write(source, b"old")
    _write(candidate, b"new")
    real_replace = migration_activation_module.durable_replace

    def fail_candidate_activation(src: Path, dst: Path) -> None:
        if src == candidate and dst == source:
            raise OSError("simulated activation failure")
        real_replace(src, dst)

    monkeypatch.setattr(
        migration_activation_module,
        "durable_replace",
        fail_candidate_activation,
    )

    with pytest.raises(MigrationActivationError, match="original database was restored"):
        activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

    assert source.read_bytes() == b"old"
    assert candidate.read_bytes() == b"new"
    assert not rollback.exists()


def test_activation_reports_failed_restore_without_claiming_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    migration_root = tmp_path / "migration"
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = (migration_root / "candidate.db").absolute()
    rollback = (migration_root / "rollback.db").absolute()
    _write(source, b"old")
    _write(candidate, b"new")
    real_replace = migration_activation_module.durable_replace

    def fail_activation_and_restore(src: Path, dst: Path) -> None:
        if src == source and dst == rollback:
            real_replace(src, dst)
            return
        raise OSError("simulated move failure")

    monkeypatch.setattr(
        migration_activation_module,
        "durable_replace",
        fail_activation_and_restore,
    )

    with pytest.raises(MigrationActivationError, match="could not be restored"):
        activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

    assert not source.exists()
    assert rollback.read_bytes() == b"old"
    assert candidate.read_bytes() == b"new"


def test_activation_refuses_reparse_boundary_before_any_move(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    migration_root = (tmp_path / "migration").absolute()
    migration_root.mkdir()
    source = (tmp_path / "athena.db").absolute()
    candidate = migration_root / "candidate.db"
    rollback = migration_root / "rollback.db"
    _write(source, b"old")
    _write(candidate, b"new")
    original = migration_activation_module.is_link_boundary

    def simulate_reparse(path: Path) -> bool:
        return path == migration_root or original(path)

    moved = False

    def fail_replace(_src: Path, _dst: Path) -> None:
        nonlocal moved
        moved = True
        raise AssertionError("no move is allowed through a reparse boundary")

    monkeypatch.setattr(migration_activation_module, "is_link_boundary", simulate_reparse)
    monkeypatch.setattr(migration_activation_module, "durable_replace", fail_replace)

    with pytest.raises(MigrationActivationError, match="reparse-point ancestor"):
        activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

    assert moved is False
    assert source.read_bytes() == b"old"
    assert candidate.read_bytes() == b"new"
