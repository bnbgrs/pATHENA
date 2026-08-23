"""Read-only classification of interrupted clone-migration artifacts."""

from __future__ import annotations

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


def _safe_regular_presence(path: Path, *, label: str) -> bool:
    if is_link_boundary(path):
        raise MigrationRecoveryError(
            f"{label} must not be a symlink, junction, or reparse point."
        )
    if not path.exists():
        return False
    if not path.is_file():
        raise MigrationRecoveryError(f"{label} is not a regular file.")
    return True


def assess_migration_recovery(
    *,
    source_db: Path,
    migration_root: Path,
) -> MigrationRecoveryAssessment:
    """Classify migration artifacts without mutating or deleting any of them."""
    source = _absolute_path(source_db, "Migration recovery source_db")
    root = _absolute_path(migration_root, "Migration recovery migration_root")
    if is_link_boundary(root) or not root.is_dir():
        raise MigrationRecoveryError("Migration recovery root must be a real directory.")
    for parent in root.parents:
        if is_link_boundary(parent):
            raise MigrationRecoveryError(
                "Migration recovery root has an unsafe path ancestor."
            )

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

    if journal.phase in {
        MigrationPhase.PREPARING,
        MigrationPhase.CLONING,
        MigrationPhase.MIGRATING,
        MigrationPhase.VERIFYING,
    }:
        state = (
            MigrationRecoveryState.INCOMPLETE
            if source_present and not rollback_present
            else MigrationRecoveryState.INCONSISTENT
        )
    elif journal.phase is MigrationPhase.READY_TO_ACTIVATE:
        state = (
            MigrationRecoveryState.READY_TO_ACTIVATE
            if source_present and candidate_present and not rollback_present
            else MigrationRecoveryState.INCONSISTENT
        )
    elif journal.phase is MigrationPhase.ACTIVATING:
        # A crash may occur between source->rollback and candidate->source, so
        # file presence alone cannot prove which database is authoritative.
        state = MigrationRecoveryState.ACTIVATION_AMBIGUOUS
    elif journal.phase is MigrationPhase.ACTIVATED:
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
