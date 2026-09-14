from __future__ import annotations

import uuid
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

from athena.backup.service import BackupService
from athena.jobs.backup import DurableBackupWorker
from athena.jobs.backup_verify_worker import BACKUP_DEEP_VERIFY_JOB_TYPE
from athena.jobs.capabilities import (
    CONTROL_LANE_JOB_TYPES,
    requires_provider_isolation,
)
from athena.jobs.models import JobPriority, JobRecord, JobState
from athena.jobs.service import DurableJobService

_ACTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_LEASE = b"r" * 32


def _deep_job() -> JobRecord:
    return JobRecord(
        job_id=uuid.uuid4(),
        job_type=BACKUP_DEEP_VERIFY_JOB_TYPE,
        created_at_us=1,
        created_by_actor_id=_ACTOR_ID,
        priority=JobPriority.MAINTENANCE,
        state=JobState.RUNNING,
        requested_scope_json=None,
        processing_run_id=None,
        current_stage=None,
        last_checkpoint_id=None,
        retry_count=0,
        next_run_at_us=None,
        blocked_reason=None,
        pinned_configuration_json=None,
        protection_scope_id=None,
        protected_payload_id=None,
        worker_id="runtime-test",
        lease_token=_LEASE,
        lease_acquired_at_us=1,
        lease_expires_at_us=10_000_000,
        heartbeat_at_us=1,
        fencing_sequence=1,
        updated_at_us=1,
    )


class _Rows:
    def fetchall(self) -> list[Any]:
        return []


class _Connection:
    def execute(self, _sql: str) -> _Rows:
        return _Rows()


def test_deep_verify_is_explicitly_control_lane() -> None:
    assert BACKUP_DEEP_VERIFY_JOB_TYPE in CONTROL_LANE_JOB_TYPES
    assert not requires_provider_isolation(BACKUP_DEEP_VERIFY_JOB_TYPE)


def test_backup_worker_delegates_leased_deep_verify_job() -> None:
    worker = object.__new__(DurableBackupWorker)
    deep_worker = Mock()
    leased = _deep_job()
    completed = replace(leased, state=JobState.COMPLETED, lease_token=None)
    deep_worker.process_leased.return_value = completed
    worker.deep_verify_worker = deep_worker

    result = worker.process_leased(leased)

    assert result is completed
    deep_worker.process_leased.assert_called_once_with(leased)


def test_backup_worker_includes_deep_verify_due_work() -> None:
    worker = object.__new__(DurableBackupWorker)
    worker.jobs = cast(DurableJobService, SimpleNamespace())
    worker.backup = cast(
        BackupService,
        SimpleNamespace(database=SimpleNamespace(connection=_Connection())),
    )
    worker.quiet_hour_utc = 3
    worker.retry_seconds = 300
    worker.lease_extension_seconds = 900
    deep_worker = Mock()
    due = _deep_job()
    deep_worker.schedule_due.return_value = (due,)
    worker.deep_verify_worker = deep_worker

    result = worker.schedule_due(now_us=20_000_000)

    assert result == (due,)
    deep_worker.schedule_due.assert_called_once_with(now_us=20_000_000)
