"""Fail-closed orchestration for clone-first SQLite schema migration."""

from __future__ import annotations

import shutil
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import is_link_boundary
from athena.storage.migration_activation import (
    MigrationActivationReport,
    activate_migration_candidate,
)
from athena.storage.migration_clone import MigrationCloneReport, create_migration_clone
from athena.storage.migration_journal import (
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
)
from athena.storage.migration_lock import migration_lock
from athena.storage.migration_safety import (
    MigrationDescriptor,
    MigrationSpacePreflight,
    assess_migration_free_space,
)

MigrationExecutor = Callable[[Path], None]


class MigrationCoordinatorError(RuntimeError):
    """Raised when automatic migration cannot proceed without recovery review."""


@dataclass(frozen=True, slots=True)
class MigrationCoordinatorResult:
    descriptor: MigrationDescriptor
    space_preflight: MigrationSpacePreflight
    clone: MigrationCloneReport
    activation: MigrationActivationReport
    final_journal: MigrationJournalState

    def __post_init__(self) -> None:
        if not isinstance(self.descriptor, MigrationDescriptor):
            raise TypeError("Migration result descriptor must be MigrationDescriptor.")
        if not isinstance(self.space_preflight, MigrationSpacePreflight):
            raise TypeError("Migration result space_preflight must be MigrationSpacePreflight.")
        if not isinstance(self.clone, MigrationCloneReport):
            raise TypeError("Migration result clone must be MigrationCloneReport.")
        if not isinstance(self.activation, MigrationActivationReport):
            raise TypeError("Migration result activation must be MigrationActivationReport.")
        if not isinstance(self.final_journal, MigrationJournalState):
            raise TypeError("Migration result final_journal must be MigrationJournalState.")
        if self.final_journal.phase is not MigrationPhase.ACTIVATED:
            raise ValueError("Migration result requires an ACTIVATED final journal state.")


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, Path):
        raise TypeError(f"{label} must be a pathlib.Path.")
    expanded = value.expanduser()
    if not expanded.is_absolute():
        raise ValueError(f"{label} must be absolute.")
    return expanded


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _assert_safe_path(path: Path, *, label: str) -> None:
    cursor = path
    while True:
        if is_link_boundary(cursor):
            raise MigrationCoordinatorError(
                f"{label} contains a symlink, junction, or reparse-point boundary."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _sqlite_sidecars(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.name}-wal"),
        path.with_name(f"{path.name}-shm"),
    )


def _assert_no_sqlite_sidecars(path: Path, *, label: str) -> None:
    if any(
        sidecar.exists() or is_link_boundary(sidecar)
        for sidecar in _sqlite_sidecars(path)
    ):
        raise MigrationCoordinatorError(
            f"{label} has SQLite WAL/SHM sidecars; recovery review is required."
        )


def _verify_migrated_candidate(
    candidate: Path,
    *,
    expected_schema_version: int,
) -> None:
    _assert_safe_path(candidate, label="Migration candidate")
    _assert_no_sqlite_sidecars(candidate, label="Migration candidate")
    try:
        connection = sqlite3.connect(
            f"{candidate.resolve(strict=True).as_uri()}?mode=ro",
            uri=True,
            timeout=5.0,
            autocommit=True,
        )
    except (OSError, sqlite3.Error) as exc:
        raise MigrationCoordinatorError(
            "Migrated candidate could not be opened read-only for verification."
        ) from exc
    try:
        connection.execute("PRAGMA query_only = ON")
        integrity = tuple(
            str(row[0])
            for row in connection.execute("PRAGMA integrity_check").fetchall()
        )
        if integrity != ("ok",):
            detail = "; ".join(integrity[:8]) or "no result"
            raise MigrationCoordinatorError(
                f"Migrated candidate integrity_check failed: {detail}"
            )
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise MigrationCoordinatorError(
                "Migrated candidate foreign_key_check reported violations."
            )
        version_row = connection.execute("PRAGMA user_version").fetchone()
        if version_row is None or int(version_row[0]) != expected_schema_version:
            raise MigrationCoordinatorError(
                "Migrated candidate schema version does not match the migration descriptor."
            )
    except MigrationCoordinatorError:
        raise
    except (sqlite3.Error, TypeError, ValueError, IndexError) as exc:
        raise MigrationCoordinatorError(
            "Migrated candidate verification could not establish integrity."
        ) from exc
    finally:
        connection.close()
    _assert_safe_path(candidate, label="Verified migration candidate")
    _assert_no_sqlite_sidecars(candidate, label="Verified migration candidate")


def run_clone_migration(
    *,
    source_db: Path,
    migration_root: Path,
    descriptor: MigrationDescriptor,
    emergency_reserve_bytes: int,
    started_at_us: int,
    executor: MigrationExecutor,
    available_bytes: int | None = None,
) -> MigrationCoordinatorResult:
    """Run one fully journaled clone migration through durable activation.

    Existing journal/candidate/rollback artifacts are never overwritten. Their
    presence means a previous attempt needs recovery analysis first.
    """
    source = _absolute_path(source_db, "Migration source_db")
    root = _absolute_path(migration_root, "Migration root")
    if not isinstance(descriptor, MigrationDescriptor):
        raise TypeError("descriptor must be MigrationDescriptor.")
    if not descriptor.requires_clone:
        raise MigrationCoordinatorError(
            "Clone migration coordinator requires descriptor.requires_clone=True."
        )
    reserve = _nonnegative_int(
        emergency_reserve_bytes,
        "Migration emergency_reserve_bytes",
    )
    started = _nonnegative_int(started_at_us, "Migration started_at_us")
    if not callable(executor):
        raise TypeError("Migration executor must be callable.")

    _assert_safe_path(source, label="Migration source")
    _assert_safe_path(root, label="Migration root")
    if not source.is_file():
        raise MigrationCoordinatorError("Migration source must be a real database file.")
    if not root.is_dir():
        raise MigrationCoordinatorError("Migration root must be a real directory.")
    _assert_no_sqlite_sidecars(source, label="Migration source")

    database_size = source.stat().st_size
    if available_bytes is None:
        free_bytes = shutil.disk_usage(source.parent).free
    else:
        free_bytes = _nonnegative_int(available_bytes, "Migration available_bytes")
    space = assess_migration_free_space(
        database_size_bytes=database_size,
        available_bytes=free_bytes,
        emergency_reserve_bytes=reserve,
    )
    if not space.sufficient:
        raise MigrationCoordinatorError(
            "Insufficient free space for clone migration and emergency reserve."
        )

    journal_store = MigrationJournalStore((root / "migration_state.json").absolute())
    candidate = (root / "candidate.db").absolute()
    rollback = (root / "rollback.db").absolute()

    with migration_lock(root):
        existing_journal = journal_store.load()
        if existing_journal is not None:
            raise MigrationCoordinatorError(
                "Existing migration journal requires recovery before a new migration."
            )
        if (
            candidate.exists()
            or rollback.exists()
            or is_link_boundary(candidate)
            or is_link_boundary(rollback)
        ):
            raise MigrationCoordinatorError(
                "Orphan migration candidate/rollback requires recovery before retry."
            )

        state = MigrationJournalState(
            migration_id=descriptor.migration_id,
            phase=MigrationPhase.PREPARING,
            source_db=source,
            candidate_db=candidate,
            started_at_us=started,
            last_completed_step="space_preflight",
        )
        journal_store.publish(state)

        state = state.advance(
            phase=MigrationPhase.CLONING,
            last_completed_step="journal_initialized",
        )
        journal_store.publish(state)
        clone = create_migration_clone(
            source_db=source,
            candidate_db=candidate,
        )
        if clone.schema_version != descriptor.from_version:
            raise MigrationCoordinatorError(
                "Migration clone source version does not match the migration descriptor."
            )

        state = state.advance(
            phase=MigrationPhase.MIGRATING,
            last_completed_step="clone_complete",
        )
        journal_store.publish(state)
        executor(candidate)

        state = state.advance(
            phase=MigrationPhase.VERIFYING,
            last_completed_step="migration_complete",
        )
        journal_store.publish(state)
        _verify_migrated_candidate(
            candidate,
            expected_schema_version=descriptor.to_version,
        )

        state = state.advance(
            phase=MigrationPhase.READY_TO_ACTIVATE,
            last_completed_step="verification_complete",
        )
        journal_store.publish(state)
        state = state.advance(
            phase=MigrationPhase.ACTIVATING,
            last_completed_step="candidate_ready",
        )
        journal_store.publish(state)
        activation = activate_migration_candidate(
            source_db=source,
            candidate_db=candidate,
            rollback_db=rollback,
        )

        state = state.advance(
            phase=MigrationPhase.ACTIVATED,
            last_completed_step="activation_complete",
        )
        journal_store.publish(state)

    return MigrationCoordinatorResult(
        descriptor=descriptor,
        space_preflight=space,
        clone=clone,
        activation=activation,
        final_journal=state,
    )
