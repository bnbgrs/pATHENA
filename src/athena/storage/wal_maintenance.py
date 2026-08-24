"""Observable, non-destructive SQLite WAL maintenance primitives."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from athena.storage.database import SQLiteDatabase
from athena.storage.durable_fs import is_link_boundary

CheckpointMode = Literal["PASSIVE", "TRUNCATE"]


class WalMaintenanceError(RuntimeError):
    """Raised when WAL state cannot be observed or checkpointed safely."""


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise WalMaintenanceError(f"{label} must be a positive integer.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise WalMaintenanceError(f"{label} must be a non-negative integer.")
    return value


def _wal_path(database_path: Path) -> Path:
    return database_path.with_name(f"{database_path.name}-wal")


def _bounded_wal_size(path: Path) -> tuple[bool, int]:
    """Read WAL size through one no-follow handle and verify path identity."""
    if is_link_boundary(path):
        raise WalMaintenanceError(
            "SQLite WAL path must not be a symlink, junction, or reparse point."
        )
    if not path.exists():
        return False, 0

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        return False, 0
    except OSError as exc:
        raise WalMaintenanceError("SQLite WAL could not be opened safely.") from exc

    try:
        handle_stat = os.fstat(descriptor)
        if not stat.S_ISREG(handle_stat.st_mode):
            raise WalMaintenanceError("SQLite WAL path is not a regular file.")
        try:
            path_stat = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise WalMaintenanceError(
                "SQLite WAL path identity could not be verified."
            ) from exc
        if not os.path.samestat(handle_stat, path_stat):
            raise WalMaintenanceError(
                "SQLite WAL path changed during size observation."
            )
        return True, _nonnegative_int(handle_stat.st_size, "SQLite WAL size")
    finally:
        os.close(descriptor)


@dataclass(frozen=True, slots=True)
class WalRuntimeStatus:
    wal_path: Path
    present: bool
    size_bytes: int
    page_size_bytes: int
    autocheckpoint_pages: int
    autocheckpoint_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.wal_path, Path) or not self.wal_path.is_absolute():
            raise ValueError("WAL status path must be absolute.")
        if not isinstance(self.present, bool):
            raise TypeError("WAL status present must be boolean.")
        _nonnegative_int(self.size_bytes, "WAL status size_bytes")
        page_size = _positive_int(self.page_size_bytes, "WAL status page_size_bytes")
        checkpoint_pages = _positive_int(
            self.autocheckpoint_pages,
            "WAL status autocheckpoint_pages",
        )
        expected_bytes = page_size * checkpoint_pages
        if self.autocheckpoint_bytes != expected_bytes:
            raise ValueError(
                "WAL status autocheckpoint_bytes must equal page_size * autocheckpoint_pages."
            )
        if not self.present and self.size_bytes != 0:
            raise ValueError("Absent WAL status must report zero size.")


@dataclass(frozen=True, slots=True)
class WalCheckpointResult:
    mode: CheckpointMode
    busy: bool
    log_frames: int
    checkpointed_frames: int
    wal_size_after_bytes: int

    def __post_init__(self) -> None:
        if self.mode not in {"PASSIVE", "TRUNCATE"}:
            raise ValueError("WAL checkpoint mode is invalid.")
        if not isinstance(self.busy, bool):
            raise TypeError("WAL checkpoint busy must be boolean.")
        _nonnegative_int(self.log_frames, "WAL checkpoint log_frames")
        checkpointed = _nonnegative_int(
            self.checkpointed_frames,
            "WAL checkpoint checkpointed_frames",
        )
        if checkpointed > self.log_frames:
            raise ValueError(
                "WAL checkpointed frame count cannot exceed the log frame count."
            )
        _nonnegative_int(
            self.wal_size_after_bytes,
            "WAL checkpoint wal_size_after_bytes",
        )

    @property
    def blocked(self) -> bool:
        return self.busy

    @property
    def complete(self) -> bool:
        return not self.busy and self.checkpointed_frames == self.log_frames


class WalMaintenanceService:
    """Observe WAL growth and invoke only SQLite-owned checkpoint primitives."""

    def __init__(self, database: SQLiteDatabase) -> None:
        if not isinstance(database, SQLiteDatabase):
            raise TypeError("WAL maintenance database must be SQLiteDatabase.")
        if not database.path.is_absolute():
            raise ValueError("WAL maintenance requires an absolute database path.")
        self.database = database

    def status(self) -> WalRuntimeStatus:
        connection = self.database.connection
        page_size_row = connection.execute("PRAGMA page_size").fetchone()
        autocheckpoint_row = connection.execute("PRAGMA wal_autocheckpoint").fetchone()
        if page_size_row is None or autocheckpoint_row is None:
            raise WalMaintenanceError("SQLite WAL policy could not be observed.")
        page_size = _positive_int(page_size_row[0], "SQLite page_size")
        autocheckpoint_pages = _positive_int(
            autocheckpoint_row[0],
            "SQLite wal_autocheckpoint",
        )
        wal_path = _wal_path(self.database.path)
        present, size_bytes = _bounded_wal_size(wal_path)
        return WalRuntimeStatus(
            wal_path=wal_path,
            present=present,
            size_bytes=size_bytes,
            page_size_bytes=page_size,
            autocheckpoint_pages=autocheckpoint_pages,
            autocheckpoint_bytes=page_size * autocheckpoint_pages,
        )

    def checkpoint_passive(self) -> WalCheckpointResult:
        """Run a non-blocking PASSIVE checkpoint and report reader interference."""
        return self._checkpoint("PASSIVE")

    def checkpoint_truncate(self, *, idle_confirmed: bool) -> WalCheckpointResult:
        """Run TRUNCATE only after the caller explicitly confirms an idle boundary."""
        if idle_confirmed is not True:
            raise WalMaintenanceError(
                "TRUNCATE checkpoint requires an explicitly confirmed idle boundary."
            )
        return self._checkpoint("TRUNCATE")

    def _checkpoint(self, mode: CheckpointMode) -> WalCheckpointResult:
        connection = self.database.connection
        if connection.in_transaction:
            raise WalMaintenanceError(
                "WAL checkpoint cannot run inside an active ATHENA transaction."
            )
        row = connection.execute(f"PRAGMA wal_checkpoint({mode})").fetchone()
        if row is None or len(row) != 3:
            raise WalMaintenanceError("SQLite returned an invalid WAL checkpoint result.")
        busy_value = _nonnegative_int(row[0], "SQLite checkpoint busy result")
        if busy_value not in {0, 1}:
            raise WalMaintenanceError("SQLite checkpoint busy result must be 0 or 1.")
        log_frames = _nonnegative_int(row[1], "SQLite checkpoint log frame count")
        checkpointed_frames = _nonnegative_int(
            row[2],
            "SQLite checkpoint completed frame count",
        )
        _present, wal_size = _bounded_wal_size(_wal_path(self.database.path))
        return WalCheckpointResult(
            mode=mode,
            busy=bool(busy_value),
            log_frames=log_frames,
            checkpointed_frames=checkpointed_frames,
            wal_size_after_bytes=wal_size,
        )
