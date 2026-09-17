from __future__ import annotations

from unittest.mock import Mock

from athena.jobs.backup_verify_durable_service import (
    BackupDeepVerifyDurableJobService,
)
from athena.jobs.backup_verify_payload import (
    BACKUP_VERIFY_DEEP_JOB_TYPE,
    BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
)
from athena.jobs.models import JobPriority
from athena.jobs.service import InvalidJobPayloadError
import pytest


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
    chat = Mock()
    chat.ensure_local_user.return_value = "actor-1"
    return BackupDeepVerifyDurableJobService(repository, chat), repository.create


def test_create_uses_durable_backup_verify_job_contract() -> None:
    create = Mock(return_value="job-42")
    service, persisted_create = _service(create=create)
    requested_scope, pinned_configuration = _valid_payload()

    job = service.create(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        priority=JobPriority.MAINTENANCE,
        requested_scope=requested_scope,
        pinned_configuration=pinned_configuration,
        next_run_at_us=1,
    )

    assert job == "job-42"
    persisted_create.assert_called_once()
    call = persisted_create.call_args.kwargs
    assert call["job_type"] == BACKUP_VERIFY_DEEP_JOB_TYPE
    assert call["actor_id"] == "actor-1"
    assert call["priority"] is JobPriority.MAINTENANCE
    assert call["next_run_at_us"] == 1


def test_create_rejects_invalid_payload_before_persistence() -> None:
    service, persisted_create = _service()
    requested_scope, pinned_configuration = _valid_payload()
    requested_scope["snapshot_id"] = "relative/path"

    with pytest.raises(InvalidJobPayloadError, match="snapshot_id"):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            requested_scope=requested_scope,
            pinned_configuration=pinned_configuration,
        )

    persisted_create.assert_not_called()


def test_create_rejects_invalid_configuration_before_persistence() -> None:
    service, persisted_create = _service()
    requested_scope, pinned_configuration = _valid_payload()
    pinned_configuration["pipeline_version"] = "wrong"

    with pytest.raises(InvalidJobPayloadError, match="pipeline_version"):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            requested_scope=requested_scope,
            pinned_configuration=pinned_configuration,
        )

    persisted_create.assert_not_called()
