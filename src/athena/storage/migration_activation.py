"""Crash-conscious activation of a verified schema-migration candidate."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import durable_replace, is_link_boundary


class MigrationActivationError(RuntimeError):
    """Raised when a migration candidate cannot be activated without data risk."""


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, Path):
        raise TypeError(f"{label} must be a pathlib.Path.")
    expanded = value.expanduser()
    if not expanded.is_absolute():
        raise ValueError(f"{label} must be absolute.")
    return expanded


def _assert_safe_existing_parent(path: Path, *, label: str) -> None:
    cursor = path.parent
    while True:
        if is_link_boundary(cursor):
            raise MigrationActivationError(
                f"{label} contains a symlink, junction, or reparse-point ancestor."
            )
        if cursor.exists() and not cursor.is_dir():
            raise MigrationActivationError(f"{label} contains a non-directory ancestor.")
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _sidecars(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.name}-wal"),
        path.with_name(f"{path.name}-shm"),
    )


def _assert_no_sidecars(path: Path, *, label: str) -> None:
    for sidecar in _sidecars(path):
        if sidecar.exists() or is_link_boundary(sidecar):
            raise MigrationActivationError(
                f"{label} has a SQLite WAL/SHM sidecar; activation is unsafe."
            )


def _assert_regular_file(path: Path, *, label: str) -> None:
    if is_link_boundary(path) or not path.is_file():
        raise MigrationActivationError(f"{label} must be a real regular file.")


def _assert_same_filesystem(paths: tuple[Path, ...]) -> None:
    try:
        devices = {os.stat(path).st_dev for path in paths}
    except OSError as exc:
        raise MigrationActivationError(
            "Migration activation filesystem identity could not be verified."
        ) from exc
    if len(devices) != 1:
        raise MigrationActivationError(
            "Migration source, candidate and rollback target must share one filesystem."
        )


@dataclass(frozen=True, slots=True)
class MigrationActivationReport:
    active_db: Path
    rollback_db: Path

    def __post_init__(self) -> None:
        active = _absolute_path(self.active_db, "Migration activation active_db")
        rollback = _absolute_path(self.rollback_db, "Migration activation rollback_db")
        if active == rollback:
            raise ValueError("Migration activation active and rollback paths must differ.")


def activate_migration_candidate(
    *,
    source_db: Path,
    candidate_db: Path,
    rollback_db: Path,
) -> MigrationActivationReport:
    """Replace the inactive live DB with a verified candidate and retain rollback.

    The caller must hold the migration lock and must have persisted the journal's
    ACTIVATING phase before entering this function. WAL/SHM sidecars are refused
    so no stale journal can be replayed against the newly activated main file.
    """
    source = _absolute_path(source_db, "Migration activation source_db")
    candidate = _absolute_path(candidate_db, "Migration activation candidate_db")
    rollback = _absolute_path(rollback_db, "Migration activation rollback_db")
    if len({source, candidate, rollback}) != 3:
        raise MigrationActivationError(
            "Migration activation source, candidate and rollback paths must differ."
        )

    for path, label in (
        (source, "Migration activation source"),
        (candidate, "Migration activation candidate"),
        (rollback, "Migration activation rollback"),
    ):
        _assert_safe_existing_parent(path, label=label)

    _assert_regular_file(source, label="Migration activation source")
    _assert_regular_file(candidate, label="Migration activation candidate")
    if rollback.exists() or is_link_boundary(rollback):
        raise MigrationActivationError(
            "Migration activation rollback target must not already exist."
        )
    if not rollback.parent.is_dir():
        raise MigrationActivationError(
            "Migration activation rollback parent must be an existing directory."
        )

    _assert_no_sidecars(source, label="Migration activation source")
    _assert_no_sidecars(candidate, label="Migration activation candidate")
    _assert_no_sidecars(rollback, label="Migration activation rollback target")
    _assert_same_filesystem((source.parent, candidate.parent, rollback.parent))

    try:
        durable_replace(source, rollback)
    except OSError as exc:
        raise MigrationActivationError(
            "Migration activation could not preserve the rollback database."
        ) from exc

    try:
        durable_replace(candidate, source)
    except BaseException as activation_exc:
        try:
            durable_replace(rollback, source)
        except BaseException as restore_exc:
            raise MigrationActivationError(
                "Migration activation failed and the original database could not be restored."
            ) from restore_exc
        if isinstance(activation_exc, Exception):
            raise MigrationActivationError(
                "Migration activation failed; the original database was restored."
            ) from activation_exc
        raise activation_exc

    _assert_regular_file(source, label="Migration activation active database")
    _assert_regular_file(rollback, label="Migration activation rollback database")
    _assert_no_sidecars(source, label="Migration activation active database")

    return MigrationActivationReport(
        active_db=source,
        rollback_db=rollback,
    )
