from __future__ import annotations

from pathlib import Path

import pytest

import athena.storage.migration_recovery as recovery_module
from athena.storage.migration_journal import (
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
)
from athena.storage.migration_recovery import (
    MigrationRecoveryError,
    MigrationRecoveryState,
    assess_migration_recovery,
)


def _paths(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    source = (tmp_path / "athena.db").absolute()
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    candidate = root / "candidate.db"
    rollback = root / "rollback.db"
    return source, root, candidate, rollback


def _publish(
    root: Path,
    *,
    source: Path,
    candidate: Path,
    phase: MigrationPhase,
) -> MigrationJournalState:
    state = MigrationJournalState(
        migration_id="schema-v1-to-v2",
        phase=phase,
        source_db=source,
        candidate_db=candidate,
        started_at_us=123,
        last_completed_step="step",
    )
    MigrationJournalStore(root / "migration_state.json").publish(state)
    return state


def test_no_artifacts_requires_no_recovery(tmp_path: Path) -> None:
    source, root, _candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"active")

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.NONE
    assert assessment.requires_manual_review is False


def test_orphan_candidate_without_journal_is_inconsistent(tmp_path: Path) -> None:
    source, root, candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"active")
    candidate.write_bytes(b"orphan")

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.INCONSISTENT
    assert assessment.requires_manual_review is True


@pytest.mark.parametrize(
    "phase",
    [
        MigrationPhase.PREPARING,
        MigrationPhase.CLONING,
        MigrationPhase.MIGRATING,
        MigrationPhase.VERIFYING,
    ],
)
def test_pre_activation_phases_keep_incomplete_recovery_state(
    tmp_path: Path,
    phase: MigrationPhase,
) -> None:
    source, root, candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"active")
    if phase is not MigrationPhase.PREPARING:
        candidate.write_bytes(b"candidate")
    _publish(root, source=source, candidate=candidate, phase=phase)

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.INCOMPLETE
    assert assessment.source_present is True
    assert assessment.rollback_present is False
    assert assessment.requires_manual_review is True


def test_ready_to_activate_requires_source_and_candidate(tmp_path: Path) -> None:
    source, root, candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"active")
    candidate.write_bytes(b"candidate")
    _publish(
        root,
        source=source,
        candidate=candidate,
        phase=MigrationPhase.READY_TO_ACTIVATE,
    )

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.READY_TO_ACTIVATE
    assert assessment.requires_manual_review is True


def test_activating_phase_is_always_ambiguous(tmp_path: Path) -> None:
    source, root, candidate, rollback = _paths(tmp_path)
    rollback.write_bytes(b"old")
    candidate.write_bytes(b"candidate")
    _publish(
        root,
        source=source,
        candidate=candidate,
        phase=MigrationPhase.ACTIVATING,
    )

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.ACTIVATION_AMBIGUOUS
    assert assessment.source_present is False
    assert assessment.rollback_present is True
    assert assessment.requires_manual_review is True


def test_activated_phase_requires_active_and_rollback_without_candidate(
    tmp_path: Path,
) -> None:
    source, root, candidate, rollback = _paths(tmp_path)
    source.write_bytes(b"new")
    rollback.write_bytes(b"old")
    _publish(
        root,
        source=source,
        candidate=candidate,
        phase=MigrationPhase.ACTIVATED,
    )

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.ACTIVATED
    assert assessment.requires_manual_review is False


def test_activated_phase_with_leftover_candidate_is_inconsistent(tmp_path: Path) -> None:
    source, root, candidate, rollback = _paths(tmp_path)
    source.write_bytes(b"new")
    candidate.write_bytes(b"leftover")
    rollback.write_bytes(b"old")
    _publish(
        root,
        source=source,
        candidate=candidate,
        phase=MigrationPhase.ACTIVATED,
    )

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.INCONSISTENT
    assert assessment.requires_manual_review is True


def test_journal_path_mismatch_is_inconsistent(tmp_path: Path) -> None:
    source, root, candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"active")
    wrong_candidate = (root / "different.db").absolute()
    _publish(
        root,
        source=source,
        candidate=wrong_candidate,
        phase=MigrationPhase.MIGRATING,
    )

    assessment = assess_migration_recovery(source_db=source, migration_root=root)

    assert assessment.state is MigrationRecoveryState.INCONSISTENT


def test_source_reparse_ancestor_is_rejected_before_artifact_classification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source, root, _candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"active")
    source_parent = source.parent
    original = recovery_module.is_link_boundary

    def simulate_reparse(path: Path) -> bool:
        return path == source_parent or original(path)

    monkeypatch.setattr(recovery_module, "is_link_boundary", simulate_reparse)

    with pytest.raises(MigrationRecoveryError, match="reparse-point boundary"):
        assess_migration_recovery(source_db=source, migration_root=root)


def test_source_replacement_after_open_fails_identity_classification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source, root, _candidate, _rollback = _paths(tmp_path)
    source.write_bytes(b"trusted")
    displaced = tmp_path / "displaced.db"
    real_assert = recovery_module._assert_safe_path
    source_checks = 0

    def racing_assert(path: Path, *, label: str) -> None:
        nonlocal source_checks
        if path == source:
            source_checks += 1
            if source_checks == 2:
                source.rename(displaced)
                source.write_bytes(b"replacement")
        real_assert(path, label=label)

    monkeypatch.setattr(recovery_module, "_assert_safe_path", racing_assert)

    with pytest.raises(MigrationRecoveryError, match="changed while recovery state"):
        assess_migration_recovery(source_db=source, migration_root=root)

    assert displaced.read_bytes() == b"trusted"
    assert source.read_bytes() == b"replacement"
