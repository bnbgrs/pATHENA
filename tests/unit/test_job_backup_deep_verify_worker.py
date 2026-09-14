from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from athena.backup.service import (
    BackupRestoreError,
    BackupService,
    BackupSnapshotRecord,
)
from athena.jobs.backup_verify_worker import (
    BACKUP_DEEP_VERIFY_JOB_TYPE,
    BackupDeepVerifyJobError,
    DurableBackupDeepVerifyWorker,
)
from athena.jobs.models import JobPriority, JobRecord, JobState, WaitingReason
from athena.jobs.service import DurableJobService

_ACTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_LEASE = b"v" * 32


def _job(
    *,
    state: JobState,
    snapshot_id: uuid.UUID,
    target_id: uuid.UUID,
    occurrence_slot_us: int,
    lease_token: bytes | None = None,
) -> JobRecord:
    scope = {
        "occurrence_slot_us": occurrence_slot_us,
        "snapshot_id": str(snapshot_id),
        "target_id": str(target_id),
    }
    configuration = {
        "interval_seconds": 5,
        "pipeline_version": "backup-deep-verify-v1",
    }
    return JobRecord(
        job_id=uuid.uuid4(),
        job_type=BACKUP_DEEP_VERIFY_JOB_TYPE,
        created_at_us=1,
        created_by_actor_id=_ACTOR_ID,
        priority=JobPriority.MAINTENANCE,
        state=state,
        requested_scope_json=json.dumps(scope, sort_keys=True, separators=(",", ":")),
        processing_run_id=None,
        current_stage=None,
        last_checkpoint_id=None,
        retry_count=0,
        next_run_at_us=None,
        blocked_reason=None,
        pinned_configuration_json=json.dumps(
            configuration,
            sort_keys=True,
            separators=(",", ":"),
        ),
        protection_scope_id=None,
        protected_payload_id=None,
        worker_id="test-worker" if lease_token is not None else None,
        lease_token=lease_token,
        lease_acquired_at_us=1 if lease_token is not None else None,
        lease_expires_at_us=10_000_000 if lease_token is not None else None,
        heartbeat_at_us=1 if lease_token is not None else None,
        fencing_sequence=1,
        updated_at_us=1,
    )


def _snapshot(
    *,
    snapshot_id: uuid.UUID,
    target_id: uuid.UUID,
    verification_status: str = "verified_light",
    last_verified_at_us: int | None = 1,
    state: str = "complete",
    pruned_at_us: int | None = None,
) -> BackupSnapshotRecord:
    return BackupSnapshotRecord(
        snapshot_id=snapshot_id,
        target_id=target_id,
        state=state,
        verification_status=verification_status,
        relative_path=f"snapshots/{snapshot_id}",
        snapshot_commit_seq=1,
        schema_version=1,
        db_sha256=b"d" * 32,
        manifest_sha256=b"m" * 32,
        object_count=0,
        created_at_us=1,
        completed_at_us=2,
        last_verified_at_us=last_verified_at_us,
        pruned_at_us=pruned_at_us,
    )


class _Database:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "CREATE TABLE backup_targets ("
            "target_id BLOB PRIMARY KEY, root_path TEXT NOT NULL, status TEXT NOT NULL)"
        )
        self.connection.execute(
            """
            CREATE TABLE backup_snapshots (
                snapshot_id BLOB PRIMARY KEY,
                target_id BLOB NOT NULL,
                state TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                completed_at_us INTEGER,
                last_verified_at_us INTEGER,
                pruned_at_us INTEGER
            )
            """
        )


class _FakeBackup:
    def __init__(
        self,
        record: BackupSnapshotRecord,
        *,
        target_status: str = "active",
    ) -> None:
        self.database = _Database()
        self.record = record
        self.current_target_status = target_status
        self.verify_calls = 0
        self.verify_error: BaseException | None = None
        self.database.connection.execute(
            "INSERT INTO backup_targets VALUES (?, ?, ?)",
            (record.target_id.bytes, str(Path("backup-target")), target_status),
        )
        self.database.connection.execute(
            "INSERT INTO backup_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.snapshot_id.bytes,
                record.target_id.bytes,
                record.state,
                record.verification_status,
                record.completed_at_us,
                record.last_verified_at_us,
                record.pruned_at_us,
            ),
        )

    def get_snapshot(self, snapshot_id: uuid.UUID) -> BackupSnapshotRecord:
        if snapshot_id != self.record.snapshot_id:
            raise BackupRestoreError("snapshot not found")
        return self.record

    def target_status(self, target_id: uuid.UUID) -> Any:
        if target_id != self.record.target_id:
            raise BackupRestoreError("target not found")
        return SimpleNamespace(status=self.current_target_status)

    def verify_deep(self, snapshot_id: uuid.UUID) -> BackupSnapshotRecord:
        self.verify_calls += 1
        if self.verify_error is not None:
            raise self.verify_error
        if snapshot_id != self.record.snapshot_id:
            raise BackupRestoreError("snapshot mismatch")
        self.record = replace(
            self.record,
            verification_status="verified_deep",
            last_verified_at_us=20_000_000,
        )
        return self.record


class _FakeJobs:
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []
        self.jobs: list[JobRecord] = []
        self.heartbeat_calls = 0
        self.checkpoints: list[dict[str, Any]] = []
        self.wait_reasons: list[WaitingReason] = []
        self.completed = 0

    def create(self, **kwargs: Any) -> JobRecord:
        self.created.append(kwargs)
        scope = cast(dict[str, Any], kwargs["requested_scope"])
        job = _job(
            state=JobState.QUEUED,
            snapshot_id=uuid.UUID(cast(str, scope["snapshot_id"])),
            target_id=uuid.UUID(cast(str, scope["target_id"])),
            occurrence_slot_us=cast(int, scope["occurrence_slot_us"]),
        )
        self.jobs.append(job)
        return job

    def active_for_type(self, job_type: str, *, limit: int = 16) -> tuple[JobRecord, ...]:
        del limit
        return tuple(
            job
            for job in self.jobs
            if job.job_type == job_type and not job.state.terminal
        )

    def list(self, *, limit: int = 100) -> tuple[JobRecord, ...]:
        return tuple(self.jobs[:limit])

    def heartbeat(self, job_id: uuid.UUID, **kwargs: Any) -> JobRecord:
        del job_id, kwargs
        self.heartbeat_calls += 1
        return self.jobs[-1] if self.jobs else cast(JobRecord, None)

    def checkpoint(self, job_id: uuid.UUID, **kwargs: Any) -> Any:
        del job_id
        self.checkpoints.append(kwargs)
        return SimpleNamespace()

    def complete(self, job_id: uuid.UUID, **kwargs: Any) -> JobRecord:
        del job_id, kwargs
        self.completed += 1
        if self.jobs:
            self.jobs[-1] = replace(self.jobs[-1], state=JobState.COMPLETED)
            return self.jobs[-1]
        raise AssertionError("test fake has no current job")

    def wait(
        self,
        job_id: uuid.UUID,
        *,
        reason: WaitingReason,
        **kwargs: Any,
    ) -> JobRecord:
        del job_id, kwargs
        self.wait_reasons.append(reason)
        if self.jobs:
            self.jobs[-1] = replace(
                self.jobs[-1],
                state=JobState.WAITING,
                blocked_reason=reason.value,
            )
            return self.jobs[-1]
        raise AssertionError("test fake has no current job")

    def acknowledge_cancel(self, job_id: uuid.UUID, **kwargs: Any) -> JobRecord:
        del job_id, kwargs
        if self.jobs:
            self.jobs[-1] = replace(self.jobs[-1], state=JobState.CANCELLED)
            return self.jobs[-1]
        raise AssertionError("test fake has no current job")


def _worker(
    jobs: _FakeJobs,
    backup: _FakeBackup,
    *,
    interval_seconds: int = 5,
) -> DurableBackupDeepVerifyWorker:
    return DurableBackupDeepVerifyWorker(
        jobs=cast(DurableJobService, jobs),
        backup=cast(BackupService, backup),
        interval_seconds=interval_seconds,
        retry_seconds=5,
        lease_extension_seconds=30,
    )


def test_deep_verify_worker_schedules_one_bounded_durable_occurrence() -> None:
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    backup = _FakeBackup(
        _snapshot(
            snapshot_id=snapshot_id,
            target_id=target_id,
            last_verified_at_us=1,
        )
    )
    jobs = _FakeJobs()
    worker = _worker(jobs, backup)

    scheduled = worker.schedule_due(now_us=10_000_000)

    assert len(scheduled) == 1
    assert len(jobs.created) == 1
    created = jobs.created[0]
    assert created["job_type"] == BACKUP_DEEP_VERIFY_JOB_TYPE
    assert created["priority"] is JobPriority.MAINTENANCE
    assert created["requested_scope"] == {
        "occurrence_slot_us": 10_000_000,
        "snapshot_id": str(snapshot_id),
        "target_id": str(target_id),
    }
    assert created["pinned_configuration"] == {
        "interval_seconds": 5,
        "pipeline_version": "backup-deep-verify-v1",
    }

    # The same occurrence is restart-safe and cannot be duplicated.
    assert worker.schedule_due(now_us=10_000_000) == ()
    assert len(jobs.created) == 1


def test_deep_verify_worker_completes_success_with_checkpoint() -> None:
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    backup = _FakeBackup(
        _snapshot(snapshot_id=snapshot_id, target_id=target_id)
    )
    jobs = _FakeJobs()
    running = _job(
        state=JobState.RUNNING,
        snapshot_id=snapshot_id,
        target_id=target_id,
        occurrence_slot_us=10_000_000,
        lease_token=_LEASE,
    )
    jobs.jobs.append(running)
    worker = _worker(jobs, backup)

    result = worker.process_leased(running)

    assert result.state is JobState.COMPLETED
    assert backup.verify_calls == 1
    assert jobs.heartbeat_calls == 1
    assert len(jobs.checkpoints) == 1
    assert jobs.checkpoints[0]["current_stage"] == "backup_deep_verify_complete"
    assert jobs.checkpoints[0]["progress_state"]["verification_status"] == "verified_deep"


def test_deep_verify_worker_waits_for_offline_target_without_verifying() -> None:
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    backup = _FakeBackup(
        _snapshot(snapshot_id=snapshot_id, target_id=target_id),
        target_status="offline",
    )
    jobs = _FakeJobs()
    running = _job(
        state=JobState.RUNNING,
        snapshot_id=snapshot_id,
        target_id=target_id,
        occurrence_slot_us=10_000_000,
        lease_token=_LEASE,
    )
    jobs.jobs.append(running)
    worker = _worker(jobs, backup)

    result = worker.process_leased(running)

    assert result.state is JobState.WAITING
    assert jobs.wait_reasons == [WaitingReason.STORAGE]
    assert backup.verify_calls == 0


def test_deep_verify_worker_treats_manual_same_occurrence_verify_as_idempotent() -> None:
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    backup = _FakeBackup(
        _snapshot(
            snapshot_id=snapshot_id,
            target_id=target_id,
            verification_status="verified_deep",
            last_verified_at_us=11_000_000,
        )
    )
    jobs = _FakeJobs()
    running = _job(
        state=JobState.RUNNING,
        snapshot_id=snapshot_id,
        target_id=target_id,
        occurrence_slot_us=10_000_000,
        lease_token=_LEASE,
    )
    jobs.jobs.append(running)
    worker = _worker(jobs, backup)

    result = worker.process_leased(running)

    assert result.state is JobState.COMPLETED
    assert backup.verify_calls == 0
    assert jobs.heartbeat_calls == 0


def test_deep_verify_worker_surfaces_integrity_failure_on_active_target() -> None:
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    backup = _FakeBackup(
        _snapshot(snapshot_id=snapshot_id, target_id=target_id)
    )
    backup.verify_error = BackupRestoreError("corrupt restore point")
    jobs = _FakeJobs()
    running = _job(
        state=JobState.RUNNING,
        snapshot_id=snapshot_id,
        target_id=target_id,
        occurrence_slot_us=10_000_000,
        lease_token=_LEASE,
    )
    jobs.jobs.append(running)
    worker = _worker(jobs, backup)

    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(running)

    assert jobs.wait_reasons == []
    assert backup.verify_calls == 1


def test_deep_verify_worker_rejects_noncanonical_scope_uuid() -> None:
    snapshot_id = uuid.UUID("a0000000-0000-0000-0000-00000000000a")
    target_id = uuid.UUID("b0000000-0000-0000-0000-00000000000b")
    backup = _FakeBackup(
        _snapshot(snapshot_id=snapshot_id, target_id=target_id)
    )
    jobs = _FakeJobs()
    running = _job(
        state=JobState.RUNNING,
        snapshot_id=snapshot_id,
        target_id=target_id,
        occurrence_slot_us=10_000_000,
        lease_token=_LEASE,
    )
    payload = json.loads(cast(str, running.requested_scope_json))
    payload["snapshot_id"] = str(snapshot_id).upper()
    running = replace(
        running,
        requested_scope_json=json.dumps(payload, sort_keys=True, separators=(",", ":")),
    )
    jobs.jobs.append(running)
    worker = _worker(jobs, backup)

    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(running)

    assert backup.verify_calls == 0


def test_deep_verify_worker_rejects_incompatible_pinned_configuration() -> None:
    snapshot_id = uuid.uuid4()
    target_id = uuid.uuid4()
    backup = _FakeBackup(
        _snapshot(snapshot_id=snapshot_id, target_id=target_id)
    )
    jobs = _FakeJobs()
    running = _job(
        state=JobState.RUNNING,
        snapshot_id=snapshot_id,
        target_id=target_id,
        occurrence_slot_us=10_000_000,
        lease_token=_LEASE,
    )
    configuration = json.loads(cast(str, running.pinned_configuration_json))
    configuration["pipeline_version"] = "backup-deep-verify-v2"
    running = replace(
        running,
        pinned_configuration_json=json.dumps(
            configuration,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
    jobs.jobs.append(running)
    worker = _worker(jobs, backup)

    with pytest.raises(BackupDeepVerifyJobError):
        worker.process_leased(running)

    assert backup.verify_calls == 0
    assert jobs.heartbeat_calls == 0
