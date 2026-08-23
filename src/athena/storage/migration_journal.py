"""Crash-durable external journal for clone-based schema migration."""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from athena.storage.durable_fs import durable_write_bytes, is_link_boundary

_MAX_MIGRATION_JOURNAL_BYTES = 64 * 1024


class MigrationJournalError(RuntimeError):
    """Raised when migration journal state cannot be trusted or published."""


class MigrationPhase(str, Enum):
    PREPARING = "preparing"
    CLONING = "cloning"
    MIGRATING = "migrating"
    VERIFYING = "verifying"
    READY_TO_ACTIVATE = "ready_to_activate"
    ACTIVATING = "activating"
    ACTIVATED = "activated"


def _canonical_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    if normalized != value:
        raise ValueError(f"{label} must use canonical trimmed text.")
    return normalized


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


def _assert_safe_parent(path: Path) -> None:
    cursor = path.parent
    while True:
        if is_link_boundary(cursor):
            raise MigrationJournalError(
                "Migration journal path contains a symlink, junction, or reparse-point ancestor."
            )
        if cursor.exists() and not cursor.is_dir():
            raise MigrationJournalError(
                "Migration journal path contains a non-directory ancestor."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _validate_journal_size(size: int) -> None:
    if size < 0 or size > _MAX_MIGRATION_JOURNAL_BYTES:
        raise MigrationJournalError(
            "Migration journal exceeds the maximum supported byte size."
        )


def _read_journal_file(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise MigrationJournalError("Migration journal could not be opened safely.") from exc
    try:
        try:
            path_stat = path.stat(follow_symlinks=False)
            handle_stat = os.fstat(descriptor)
        except OSError as exc:
            raise MigrationJournalError(
                "Migration journal file identity could not be verified."
            ) from exc
        if is_link_boundary(path) or not os.path.samestat(path_stat, handle_stat):
            raise MigrationJournalError(
                "Migration journal pathname changed while it was being opened."
            )
        if not stat.S_ISREG(handle_stat.st_mode):
            raise MigrationJournalError("Migration journal path is not a regular file.")
        _validate_journal_size(int(handle_stat.st_size))
        try:
            handle = os.fdopen(descriptor, "rb", closefd=True)
        except OSError as exc:
            raise MigrationJournalError(
                "Migration journal file handle could not be created."
            ) from exc
        descriptor = -1
        try:
            payload = handle.read(_MAX_MIGRATION_JOURNAL_BYTES + 1)
        except OSError as exc:
            raise MigrationJournalError("Migration journal could not be read.") from exc
        finally:
            handle.close()
        _validate_journal_size(len(payload))
        return payload
    finally:
        if descriptor >= 0:
            os.close(descriptor)


@dataclass(frozen=True, slots=True)
class MigrationJournalState:
    """Minimal external recovery facts for one schema migration attempt."""

    migration_id: str
    phase: MigrationPhase
    source_db: Path
    candidate_db: Path
    started_at_us: int
    last_completed_step: str | None

    def __post_init__(self) -> None:
        _canonical_text(self.migration_id, "Migration journal migration_id")
        if not isinstance(self.phase, MigrationPhase):
            raise TypeError("Migration journal phase must be MigrationPhase.")
        source = _absolute_path(self.source_db, "Migration journal source_db")
        candidate = _absolute_path(self.candidate_db, "Migration journal candidate_db")
        if source == candidate:
            raise ValueError("Migration journal source and candidate databases must differ.")
        _nonnegative_int(self.started_at_us, "Migration journal started_at_us")
        if self.last_completed_step is not None:
            _canonical_text(
                self.last_completed_step,
                "Migration journal last_completed_step",
            )

    def advance(
        self,
        *,
        phase: MigrationPhase,
        last_completed_step: str | None,
    ) -> "MigrationJournalState":
        if not isinstance(phase, MigrationPhase):
            raise TypeError("Migration journal phase must be MigrationPhase.")
        if phase_order(phase) < phase_order(self.phase):
            raise MigrationJournalError("Migration journal phase must not move backwards.")
        return MigrationJournalState(
            migration_id=self.migration_id,
            phase=phase,
            source_db=self.source_db,
            candidate_db=self.candidate_db,
            started_at_us=self.started_at_us,
            last_completed_step=last_completed_step,
        )


def phase_order(phase: MigrationPhase) -> int:
    if not isinstance(phase, MigrationPhase):
        raise TypeError("Migration phase must be MigrationPhase.")
    return tuple(MigrationPhase).index(phase)


def _reject_constant(value: str) -> object:
    raise MigrationJournalError(
        f"Migration journal contains non-standard JSON constant {value!r}."
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise MigrationJournalError(
                f"Migration journal contains duplicate JSON key {key!r}."
            )
        result[key] = value
    return result


def encode_migration_journal(state: MigrationJournalState) -> bytes:
    if not isinstance(state, MigrationJournalState):
        raise TypeError("state must be MigrationJournalState.")
    payload = {
        "candidate_db": str(state.candidate_db),
        "last_completed_step": state.last_completed_step,
        "migration_id": state.migration_id,
        "phase": state.phase.value,
        "source_db": str(state.source_db),
        "started_at_us": state.started_at_us,
    }
    encoded = (
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    _validate_journal_size(len(encoded))
    return encoded


def decode_migration_journal(payload: bytes) -> MigrationJournalState:
    if not isinstance(payload, bytes):
        raise TypeError("Migration journal payload must be bytes.")
    _validate_journal_size(len(payload))
    try:
        value = json.loads(
            payload.decode("utf-8"),
            parse_constant=_reject_constant,
            object_pairs_hook=_unique_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MigrationJournalError("Migration journal is not valid canonical JSON.") from exc
    if not isinstance(value, dict):
        raise MigrationJournalError("Migration journal root must be a JSON object.")
    required = {
        "candidate_db",
        "last_completed_step",
        "migration_id",
        "phase",
        "source_db",
        "started_at_us",
    }
    if set(value) != required:
        raise MigrationJournalError("Migration journal fields do not match the v1 contract.")
    try:
        phase = MigrationPhase(value["phase"])
    except (TypeError, ValueError) as exc:
        raise MigrationJournalError("Migration journal phase is unsupported.") from exc
    try:
        source_db = Path(value["source_db"])
        candidate_db = Path(value["candidate_db"])
    except TypeError as exc:
        raise MigrationJournalError("Migration journal database paths must be text.") from exc
    try:
        return MigrationJournalState(
            migration_id=value["migration_id"],
            phase=phase,
            source_db=source_db,
            candidate_db=candidate_db,
            started_at_us=value["started_at_us"],
            last_completed_step=value["last_completed_step"],
        )
    except (TypeError, ValueError) as exc:
        raise MigrationJournalError("Migration journal state is invalid.") from exc


class MigrationJournalStore:
    """Publish and recover one migration_state.json outside the candidate DB."""

    def __init__(self, path: Path) -> None:
        self.path = _absolute_path(path, "Migration journal path")

    def load(self) -> MigrationJournalState | None:
        _assert_safe_parent(self.path)
        if is_link_boundary(self.path):
            raise MigrationJournalError(
                "Migration journal path must not be a symlink, junction, or reparse point."
            )
        if not self.path.exists():
            return None
        if not self.path.is_file():
            raise MigrationJournalError("Migration journal path is not a regular file.")
        payload = _read_journal_file(self.path)
        return decode_migration_journal(payload)

    def publish(self, state: MigrationJournalState) -> None:
        if not isinstance(state, MigrationJournalState):
            raise TypeError("state must be MigrationJournalState.")
        data = encode_migration_journal(state)
        _assert_safe_parent(self.path)
        parent = self.path.parent
        if not parent.is_dir() or is_link_boundary(parent):
            raise MigrationJournalError("Migration journal parent must be a real directory.")
        if is_link_boundary(self.path):
            raise MigrationJournalError(
                "Migration journal path must not be a symlink, junction, or reparse point."
            )
        try:
            durable_write_bytes(self.path, data, mode=0o600)
        except (OSError, TypeError, ValueError) as exc:
            raise MigrationJournalError("Migration journal could not be published durably.") from exc
