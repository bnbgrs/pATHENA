from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest

from athena.backup.service import BackupRestoreError
from athena.backup.target_lock import BackupTargetBusyError
from athena.jobs.backup_verify_worker import (
    BACKUP_VERIFY_DEEP_JOB_TYPE,
    BackupDeepVerifyJobError,
    DurableBackupDeepVerifyWorker,
)
from athena.jobs.models import JobState, WaitingReason


@dataclass
class FakeJobs:
    calls: list[tuple[str, dict[str, object]]] = field(default_factory=list)

    def acknowledge_cancel(self, job_id, **kwargs):
        self.calls.append(("cancel", kwargs))
        return SimpleNamespace(job_id=job_id, state=JobState.CANCELLED)

    def heartbeat(self, job_id, **kwargs):
        self.calls.append(("heartbeat", kwargs))
        return SimpleNamespace(job_id=job_id)

    def wait(self, job_id, **kwargs):
        self.calls.append(("wait", kwargs))
        return SimpleNamespace(job_id=job_id, state=JobState.WAITING)

    def checkpoint(self, job_id, **kwargs):
        self.calls.append(("checkpoint", kwargs))
        return SimpleNamespace(job_id=job_id)

    def complete(self, job_id, **kwargs):
        self.calls.append(("complete", kwargs))
        return SimpleNamespace(job_id=job_id, state=JobState.COMPLETED)


@dataclass
class FakeBackup:
    snapshot_id: uuid.UUID
    target_id: uuid.UUID
    target_status_value: str = "active"
    outcome: str = "ok"
    verify_calls: list[uuid.UUID] = field(default_factory=list)

    def get_snapshot(self, snapshot_id):
        assert snapshot_id == self.snapshot_id
        return SimpleNamespace(snapshot_id=snapshot_id, target_id=self.target_id)

    def target_status(self, target_id):
        assert target_id == self.target_id
        return SimpleNamespace(status=self.target_status_value)

    def verify_deep(self, snapshot_id):
        self.verify_calls.append(snapshot_id)
        if self.outcome == "busy":
            raise BackupTargetBusyError("busy")
        if self.outcome == "oserror":
            raise OSError("offline")
        if self.outcome == "corrupt":
            raise BackupRestoreError("corrupt")
        return SimpleNamespace(
            snapshot_id=snapshot_id,
            target_id=self.target_id,
            verification_status="verified_deep",
        )


def _case(*, outcome="ok", target_status="active", state=JobState.RUNNING):
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    jobs = FakeJobs()
    backup = FakeBackup(
        snapshot_id=snapshot_id,
        target_id=target_id,
        target_status_value=target_status,
        outcome=outcome,
    )
    worker = DurableBackupDeepVerifyWorker(
        jobs=jobs,
        backup=backup,
        retry_seconds=5,
    )
    job = SimpleNamespace(
        job_id=uuid.uuid4(),
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        state=state,
        lease_token=b"lease",
        requested_scope_json=json.dumps({"snapshot_id": str(snapshot_id)}),
    )
    return worker, job, jobs, backup


def test_success_checkpoints_and_completes_without_backup_creation() -> None:
    worker, job, jobs, backup = _case()
    result = worker.process_leased(job)
    assert result.state is JobState.COMPLETED
    assert backup.verify_calls == [backup.snapshot_id]
    assert [name for name, _ in jobs.calls] == ["heartbeat", "checkpoint", "complete"]


def test_busy_target_waits_with_backoff() -> None:
    worker, job, jobs, _ = _case(outcome="busy")
    result = worker.process_leased(job)
    assert result.state is JobState.WAITING
    assert jobs.calls[-1][1]["reason"] is WaitingReason.BACKOFF


def test_environment_error_waits_for_storage() -> None:
    worker, job, jobs, _ = _case(outcome="oserror")
    result = worker.process_leased(job)
    assert result.state is JobState.WAITING
    assert jobs.calls[-1][1]["reason"] is WaitingReason.STORAGE


def test_offline_target_waits_without_verification() -> None:
    worker, job, jobs, backup = _case(target_status="offline")
    result = worker.process_leased(job)
    assert result.state is JobState.WAITING
    assert jobs.calls[-1][1]["reason"] is WaitingReason.STORAGE
    assert backup.verify_calls == []


def test_corrupt_active_snapshot_fails_closed() -> None:
    worker, job, jobs, _ = _case(outcome="corrupt")
    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(job)
    assert [name for name, _ in jobs.calls] == ["heartbeat"]


def test_cancel_is_acknowledged_before_verification() -> None:
    worker, job, _, backup = _case(state=JobState.CANCEL_REQUESTED)
    result = worker.process_leased(job)
    assert result.state is JobState.CANCELLED
    assert backup.verify_calls == []
