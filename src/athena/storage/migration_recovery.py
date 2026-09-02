"""Read-only classification of interrupted clone-migration artifacts."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from athena.storage.durable_fs import is_link_boundary
from athena.storage.migration_journal import (
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
)


class MigrationRecoveryError(RuntimeError):
    """Raised when migration recovery artifacts cannot be classified safely."""


class MigrationRecoveryState(str, Enum):
    NONE = "none"
    INCOMPLETE = "incomplete"
    READY_TO_ACTIVATE = "ready_to_activate"
    ACTIVATION_AMBIGUOUS = "activation_ambiguous"
    ACTIVATED = "activated"
    INCONSISTENT = "inconsistent"


@dataclass(frozen=True, slots=True)
class MigrationRecoveryAssessment:
    state: MigrationRecoveryState
    journal: MigrationJournalState | None
    source_present: bool
    candidate_present: bool
    rollback_present: bool

    def __post_init__(self) -> None:
        if not isinstance(self.state, MigrationRecoveryState):
            raise TypeError("Migration recovery state must be MigrationRecoveryState.")
        if self.journal is not None and not isinstance(self.journal, MigrationJournalState):
            raise TypeError("Migration recovery journal must be MigrationJournalState or None.")
        for value, label in (
            (self.source_present, "source_present"),
            (self.candidate_present, "candidate_present"),
            (self.rollback_present, "rollback_present"),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"Migration recovery {label} must be bool.")
        if self.state is MigrationRecoveryState.NONE and self.journal is not None:
            raise ValueError("Migration recovery NONE must not carry a journal.")

    @property
    def requires_manual_review(self) -> bool:
        return self.state not in {MigrationRecoveryState.NONE, MigrationRecoveryState.ACTIVATED}


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, Path):
        raise TypeError(f"{label} must be a pathlib.Path.")
    expanded = value.expanduser()
    if not expanded.is_absolute():
        raise ValueError(f"{label} must be absolute.")
    return expanded


def _assert_safe_path(path: Path, *, label: str) -> None:
    for candidate in (path, *path.parents):
        if is_link_boundary(candidate):
            raise MigrationRecoveryError(
                f"{label} contains a symlink, junction, or reparse-point boundary."
            )
        if candidate != path and candidate.exists() and not candidate.is_dir():
            raise MigrationRecoveryError(f"{label} contains a non-directory ancestor.")


def _safe_regular_presence(path: Path, *, label: str) -> bool:
    """Classify one artifact through a no-follow opened-file identity."""
    _assert_safe_path(path, label=label)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise MigrationRecoveryError(f"{label} could not be opened safely.") from exc

    try:
        handle_stat = os.fstat(descriptor)
        if not stat.S_ISREG(handle_stat.st_mode):
            raise MigrationRecoveryError(f"{label} is not a regular file.")

        # Re-check path boundaries after acquiring the handle, then prove the
        # pathname still denotes that same opened regular file. A concurrent
        # rename/replacement is therefore an integrity error, not a presence
        # classification based on mixed filesystem snapshots.
        _assert_safe_path(path, label=label)
        try:
            path_stat = os.lstat(path)
        except FileNotFoundError as exc:
            raise MigrationRecoveryError(
                f"{label} changed while recovery state was being classified."
            ) from exc
        except OSError as exc:
            raise MigrationRecoveryError(
                f"{label} identity could not be verified."
            ) from exc

        if not stat.S_ISREG(path_stat.st_mode) or not os.path.samestat(
            handle_stat,
            path_stat,
        ):
            raise MigrationRecoveryError(
                f"{label} changed while recovery state was being classified."
            )
        return True
    finally:
        os.close(descriptor)


def assess_migration_recovery(
    *,
    source_db: Path,
    migration_root: Path,
) -> MigrationRecoveryAssessment:
    """Classify migration artifacts without mutating or deleting any of them."""
    source = _absolute_path(source_db, "Migration recovery source_db")
    root = _absolute_path(migration_root, "Migration recovery migration_root")
    _assert_safe_path(root, label="Migration recovery root")
    if not root.is_dir():
        raise MigrationRecoveryError("Migration recovery root must be a real directory.")

    journal_store = MigrationJournalStore((root / "migration_state.json").absolute())
    journal = journal_store.load()
    candidate = (root / "candidate.db").absolute()
    rollback = (root / "rollback.db").absolute()

    source_present = _safe_regular_presence(
        source,
        label="Migration recovery source database",
    )
    candidate_present = _safe_regular_presence(
        candidate,
        label="Migration recovery candidate database",
    )
    rollback_present = _safe_regular_presence(
        rollback,
        label="Migration recovery rollback database",
    )

    if journal is None:
        if candidate_present or rollback_present:
            state = MigrationRecoveryState.INCONSISTENT
        else:
            state = MigrationRecoveryState.NONE
        return MigrationRecoveryAssessment(
            state=state,
            journal=None,
            source_present=source_present,
            candidate_present=candidate_present,
            rollback_present=rollback_present,
        )

    if journal.source_db != source or journal.candidate_db != candidate:
        return MigrationRecoveryAssessment(
            state=MigrationRecoveryState.INCONSISTENT,
            journal=journal,
            source_present=source_present,
            candidate_present=candidate_present,
            rollback_present=rollback_present,
        )

    # Branch on persisted string values rather than exhaustively on the enum so
    # an unexpected future phase remains a reachable fail-closed path at runtime.
    phase = journal.phase.value
    if phase in {
        MigrationPhase.PREPARING.value,
        MigrationPhase.CLONING.value,
        MigrationPhase.MIGRATING.value,
        MigrationPhase.VERIFYING.value,
    }:
        state = (
            MigrationRecoveryState.INCOMPLETE
            if source_present and not rollback_present
            else MigrationRecoveryState.INCONSISTENT
        )
    elif phase == MigrationPhase.READY_TO_ACTIVATE.value:
        state = (
            MigrationRecoveryState.READY_TO_ACTIVATE
            if source_present and candidate_present and not rollback_present
            else MigrationRecoveryState.INCONSISTENT
        )
    elif phase == MigrationPhase.ACTIVATING.value:
        # A crash may occur between source->rollback and candidate->source, so
        # file presence alone cannot prove which database is authoritative.
        state = MigrationRecoveryState.ACTIVATION_AMBIGUOUS
    elif phase == MigrationPhase.ACTIVATED.value:
        state = (
            MigrationRecoveryState.ACTIVATED
            if source_present and rollback_present and not candidate_present
            else MigrationRecoveryState.INCONSISTENT
        )
    else:
        state = MigrationRecoveryState.INCONSISTENT

    return MigrationRecoveryAssessment(
        state=state,
        journal=journal,
        source_present=source_present,
        candidate_present=candidate_present,
        rollback_present=rollback_present,
    )
