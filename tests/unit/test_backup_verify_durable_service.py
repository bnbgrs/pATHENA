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


def _service(
    *,
    create: Mock | None = None,
) -> tuple[BackupDeepVerifyDurableJobService, Mock]:
    repository = Mock()
    repository.create = create or Mock(return_value="job-1")
    service = BackupDeepVerifyDurableJobService(repository=repository)
    return service, repository


def test_submit_creates_durable_backup_verify_job() -> None:
    service, repository = _service()
    payload, metadata = _valid_payload()

    job_id = service.submit(payload=payload, metadata=metadata)

    assert job_id == "job-1"
    repository.create.assert_called_once_with(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        payload=payload,
        metadata=metadata,
        priority=JobPriority.NORMAL,
    )


def test_submit_rejects_invalid_payload_before_create() -> None:
    service, repository = _service()
    payload, metadata = _valid_payload()
    payload["snapshot_id"] = "invalid"

    with pytest.raises(InvalidJobPayloadError):
        service.submit(payload=payload, metadata=metadata)

    repository.create.assert_not_called()


def test_submit_propagates_repository_failure() -> None:
    create = Mock(side_effect=RuntimeError("repository failure"))
    service, _repository = _service(create=create)
    payload, metadata = _valid_payload()

    with pytest.raises(RuntimeError, match="repository failure"):
        service.submit(payload=payload, metadata=metadata)
