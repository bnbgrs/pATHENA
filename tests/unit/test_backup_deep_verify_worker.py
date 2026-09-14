from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest

from athena.backup.service import BackupRestoreError
from athena.backup.target_lock import BackupTargetBusyError
from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_PIPELINE_VERSION
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


def _case(
    *,
    outcome="ok",
    target_status="active",
    state=JobState.RUNNING,
    requested_scope=None,
    pinned_configuration=None,
):
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
    if requested_scope is None:
        requested_scope = {
            "snapshot_id": str(snapshot_id),
            "occurrence_slot_us": 123_000_000,
        }
    if pinned_configuration is None:
        pinned_configuration = {
            "pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
        }
    job = SimpleNamespace(
        job_id=uuid.uuid4(),
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        state=state,
        lease_token=b"lease",
        requested_scope_json=json.dumps(requested_scope),
        pinned_configuration_json=json.dumps(pinned_configuration),
    )
    return worker, job, jobs, backup


def test_success_checkpoints_and_completes_without_backup_creation() -> None:
    worker, job, jobs, backup = _case()
    result = worker.process_leased(job)
    assert result.state is JobState.COMPLETED
    assert backup.verify_calls == [backup.snapshot_id]
    assert [name for name, _ in jobs.calls] == ["heartbeat", "checkpoint", "complete"]
    checkpoint = jobs.calls[1][1]
    assert checkpoint["progress_state"]["occurrence_slot_us"] == 123_000_000
    assert checkpoint["last_confirmed_output"]["occurrence_slot_us"] == 123_000_000


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


def test_cancel_is_acknowledged_before_payload_validation() -> None:
    worker, job, _, backup = _case(
        state=JobState.CANCEL_REQUESTED,
        requested_scope={},
    )
    result = worker.process_leased(job)
    assert result.state is JobState.CANCELLED
    assert backup.verify_calls == []


@pytest.mark.parametrize(
    "requested_scope",
    [
        {"snapshot_id": str(uuid.uuid4())},
        {"snapshot_id": str(uuid.uuid4()), "occurrence_slot_us": True},
        {
            "snapshot_id": str(uuid.uuid4()),
            "occurrence_slot_us": 0,
            "extra": "x",
        },
    ],
)
def test_malformed_requested_scope_fails_before_backup_access(
    requested_scope,
) -> None:
    worker, job, _, backup = _case(requested_scope=requested_scope)
    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(job)
    assert backup.verify_calls == []


def test_wrong_pipeline_version_fails_before_backup_access() -> None:
    worker, job, _, backup = _case(
        pinned_configuration={"pipeline_version": "backup-deep-verify-v0"},
    )
    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(job)
    assert backup.verify_calls == []


def test_missing_pinned_configuration_fails_before_backup_access() -> None:
    worker, job, _, backup = _case()
    job.pinned_configuration_json = None
    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(job)
    assert backup.verify_calls == []
