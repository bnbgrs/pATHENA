from __future__ import annotations

from unittest.mock import Mock

import pytest

from athena.jobs.backup_verify_durable_service import BackupDeepVerifyDurableJobService
from athena.jobs.backup_verify_payload import (
    BACKUP_VERIFY_DEEP_JOB_TYPE,
    BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
)
from athena.jobs.models import JobPriority
from athena.jobs.service import InvalidJobPayloadError


_SNAPSHOT_ID = "12345678-1234-5678-9234-567812345678"


def _valid_payload() -> tuple[dict[str, object], dict[str, object]]:
    return (
        {"snapshot_id": _SNAPSHOT_ID, "occurrence_slot_us": 1},
        {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION},
    )


def test_create_persists_maintenance_job() -> None:
    repository = Mock()
    service = BackupDeepVerifyDurableJobService(repository=repository)

    job = service.create(
        job_id="backup-verify-deep:12345678-1234-5678-9234-567812345678:1",
        payload={"snapshot_id": _SNAPSHOT_ID, "occurrence_slot_us": 1},
        next_run_at_us=123,
    )

    assert job.type == BACKUP_VERIFY_DEEP_JOB_TYPE
    assert job.priority == JobPriority.MAINTENANCE
    assert job.next_run_at_us == 123
    assert job.payload == {"snapshot_id": _SNAPSHOT_ID, "occurrence_slot_us": 1}
    assert job.metadata == {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION}
    repository.create.assert_called_once_with(job)


def test_create_rejects_invalid_payload_before_persisting() -> None:
    repository = Mock()
    service = BackupDeepVerifyDurableJobService(repository=repository)

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_id="backup-verify-deep:invalid:1",
            payload={"snapshot_id": "not-a-uuid", "occurrence_slot_us": 1},
            next_run_at_us=123,
        )

    repository.create.assert_not_called()


def test_create_rejects_invalid_metadata_before_persisting() -> None:
    repository = Mock()
    service = BackupDeepVerifyDurableJobService(repository=repository)
    payload, _metadata = _valid_payload()

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_id="backup-verify-deep:12345678-1234-5678-9234-567812345678:1",
            payload=payload,
            next_run_at_us=123,
            metadata={"pipeline_version": "wrong"},
        )

    repository.create.assert_not_called()
