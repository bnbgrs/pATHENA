from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Iterator, cast

import pytest

import athena.jobs.backup_verify_worker as worker_module
from athena.backup.retention import BackupRetentionPolicy, BackupTargetRecord
from athena.backup.service import BackupService
from athena.backup.target_lock import BackupTargetBusyError
from athena.jobs.backup_verify import BackupDeepVerifyCandidate
from athena.jobs.backup_verify_worker import (
    BACKUP_DEEP_VERIFY_JOB_TYPE,
    DurableBackupDeepVerifyWorker,
)
from athena.jobs.models import JobRecord
from athena.jobs.service import DurableJobService


@dataclass
class _LockState:
    held: bool = False


class _FakeBackup:
    def __init__(self, target: BackupTargetRecord, lock_state: _LockState) -> None:
        self.target = target
        self.lock_state = lock_state
        self.get_target_calls: list[bool] = []

    def get_target(self, target_id: uuid.UUID) -> BackupTargetRecord:
        assert target_id == self.target.target_id
        self.get_target_calls.append(self.lock_state.held)
        return self.target


class _FakeJobs:
    def __init__(self, lock_state: _LockState) -> None:
        self.lock_state = lock_state
        self.created = 0
        self.active_jobs: tuple[JobRecord, ...] = ()
        self.created_record = cast(JobRecord, object())

    def active_for_type(
        self,
        job_type: str,
        *,
        limit: int = 16,
    ) -> tuple[JobRecord, ...]:
        assert self.lock_state.held
        assert job_type == BACKUP_DEEP_VERIFY_JOB_TYPE
        assert limit > 0
        return self.active_jobs

    def list(self, *, limit: int = 100) -> tuple[JobRecord, ...]:
        assert self.lock_state.held
        assert limit > 0
        return ()

    def create(self, **_kwargs: object) -> JobRecord:
        assert self.lock_state.held
        self.created += 1
        return self.created_record


def _target(tmp_path: Path, target_id: uuid.UUID) -> BackupTargetRecord:
    root = tmp_path / "backup"
    root.mkdir()
    return BackupTargetRecord(
        target_id=target_id,
        root_path=root,
        status="active",
        policy=BackupRetentionPolicy(),
        identity_initialized=True,
        created_at_us=1,
        last_successful_backup_at_us=None,
        last_verified_at_us=None,
    )


def _candidate(target_id: uuid.UUID) -> BackupDeepVerifyCandidate:
    return BackupDeepVerifyCandidate(
        snapshot_id=uuid.uuid4(),
        target_id=target_id,
        completed_at_us=1,
        last_verified_at_us=None,
        occurrence_slot_us=10_000_000,
    )


def _worker(
    backup: _FakeBackup,
    jobs: _FakeJobs,
) -> DurableBackupDeepVerifyWorker:
    return DurableBackupDeepVerifyWorker(
        backup=cast(BackupService, backup),
        jobs=cast(DurableJobService, jobs),
        interval_seconds=10,
    )


def test_schedule_due_reselects_and_creates_only_inside_target_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_id = uuid.uuid4()
    state = _LockState()
    backup = _FakeBackup(_target(tmp_path, target_id), state)
    jobs = _FakeJobs(state)
    candidate = _candidate(target_id)
    selection_lock_states: list[bool] = []

    def select_candidate(*_args: object, **_kwargs: object) -> BackupDeepVerifyCandidate:
        selection_lock_states.append(state.held)
        return candidate

    @contextmanager
    def serialized_lock(path: Path) -> Iterator[None]:
        assert path == backup.target.root_path
        assert not state.held
        state.held = True
        try:
            yield
        finally:
            state.held = False

    monkeypatch.setattr(worker_module, "select_deep_verify_candidate", select_candidate)
    monkeypatch.setattr(worker_module, "backup_target_lock", serialized_lock)

    result = _worker(backup, jobs).schedule_due(now_us=10_000_000)

    assert result == (jobs.created_record,)
    assert jobs.created == 1
    assert selection_lock_states == [False, True]
    assert backup.get_target_calls == [False, True]
    assert not state.held


def test_schedule_due_rechecks_due_state_after_lock_acquisition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_id = uuid.uuid4()
    state = _LockState()
    backup = _FakeBackup(_target(tmp_path, target_id), state)
    jobs = _FakeJobs(state)
    candidate = _candidate(target_id)
    selections: list[BackupDeepVerifyCandidate | None] = [candidate, None]

    def select_candidate(
        *_args: object,
        **_kwargs: object,
    ) -> BackupDeepVerifyCandidate | None:
        return selections.pop(0)

    @contextmanager
    def serialized_lock(_path: Path) -> Iterator[None]:
        state.held = True
        try:
            yield
        finally:
            state.held = False

    monkeypatch.setattr(worker_module, "select_deep_verify_candidate", select_candidate)
    monkeypatch.setattr(worker_module, "backup_target_lock", serialized_lock)

    assert _worker(backup, jobs).schedule_due(now_us=10_000_000) == ()
    assert jobs.created == 0
    assert selections == []


def test_schedule_due_observes_competing_reservation_inside_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_id = uuid.uuid4()
    state = _LockState()
    backup = _FakeBackup(_target(tmp_path, target_id), state)
    jobs = _FakeJobs(state)
    candidate = _candidate(target_id)

    def select_candidate(*_args: object, **_kwargs: object) -> BackupDeepVerifyCandidate:
        return candidate

    @contextmanager
    def serialized_lock(_path: Path) -> Iterator[None]:
        state.held = True
        jobs.active_jobs = (
            cast(
                JobRecord,
                SimpleNamespace(
                    requested_scope_json=json.dumps(
                        {
                            "occurrence_slot_us": candidate.occurrence_slot_us,
                            "snapshot_id": str(candidate.snapshot_id),
                            "target_id": str(candidate.target_id),
                        }
                    )
                ),
            ),
        )
        try:
            yield
        finally:
            state.held = False

    monkeypatch.setattr(worker_module, "select_deep_verify_candidate", select_candidate)
    monkeypatch.setattr(worker_module, "backup_target_lock", serialized_lock)

    assert _worker(backup, jobs).schedule_due(now_us=10_000_000) == ()
    assert jobs.created == 0


def test_schedule_due_busy_target_does_not_persist_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_id = uuid.uuid4()
    state = _LockState()
    backup = _FakeBackup(_target(tmp_path, target_id), state)
    jobs = _FakeJobs(state)
    candidate = _candidate(target_id)

    def select_candidate(*_args: object, **_kwargs: object) -> BackupDeepVerifyCandidate:
        return candidate

    @contextmanager
    def busy_lock(_path: Path) -> Iterator[None]:
        raise BackupTargetBusyError("busy")
        yield

    monkeypatch.setattr(worker_module, "select_deep_verify_candidate", select_candidate)
    monkeypatch.setattr(worker_module, "backup_target_lock", busy_lock)

    assert _worker(backup, jobs).schedule_due(now_us=10_000_000) == ()
    assert jobs.created == 0
