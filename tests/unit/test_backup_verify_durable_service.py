from __future__ import annotations

from unittest.mock import Mock

import pytest

from athena.jobs.backup_verify_durable_service import BackupDeepVerifyDurableJobService
from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.models import JobPriority
from athena.jobs.service import InvalidJobPayloadError


_SNAPSHOT_ID = "12345678-1234-5678-9234-567812345678"


def _valid_payload() -> tuple[dict[str, object], dict[str, object]]:
    return (
        {"snapshot_id": _SNAPSHOT_ID, "occurrence_slot_us": 1},
        {
            "snapshot_id": _SNAPSHOT_ID,
            "occurrence_slot_us": 1,
            "retry_via_backup_create": False,
        },
    )


def test_deep_verify_rejects_malformed_payload_before_side_effects() -> None:
    repository = Mock()
    actors = Mock()
    canonical_service = Mock()
    service = BackupDeepVerifyDurableJobService(
        repository=repository,
        actors=actors,
        canonical_service=canonical_service,
    )

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            requested_scope={"snapshot_id": "not-a-uuid", "occurrence_slot_us": 1},
            priority=JobPriority.TIME_CRITICAL,
        )

    actors.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()
    canonical_service.create.assert_not_called()


def test_deep_verify_persists_validated_payload_once() -> None:
    requested_scope, normalized_scope = _valid_payload()
    repository = Mock()
    repository.create.return_value = "job-1"
    actors = Mock()
    actors.ensure_local_user.return_value = "actor-1"
    canonical_service = Mock()
    service = BackupDeepVerifyDurableJobService(
        repository=repository,
        actors=actors,
        canonical_service=canonical_service,
    )

    result = service.create(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        requested_scope=requested_scope,
        priority=JobPriority.TIME_CRITICAL,
    )

    assert result == "job-1"
    actors.ensure_local_user.assert_called_once_with()
    repository.create.assert_called_once_with(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        requested_scope=normalized_scope,
        priority=JobPriority.TIME_CRITICAL,
        actor_id="actor-1",
    )
    canonical_service.create.assert_not_called()


def test_non_deep_verify_job_delegates_to_canonical_service_validation() -> None:
    repository = Mock()
    actors = Mock()
    canonical_service = Mock()
    canonical_service.create.side_effect = InvalidJobPayloadError("invalid backup.create payload")
    service = BackupDeepVerifyDurableJobService(
        repository=repository,
        actors=actors,
        canonical_service=canonical_service,
    )

    with pytest.raises(InvalidJobPayloadError, match="invalid backup.create payload"):
        service.create(
            job_type="backup.create",
            requested_scope={},
            priority=JobPriority.NORMAL,
        )

    canonical_service.create.assert_called_once_with(
        job_type="backup.create",
        requested_scope={},
        priority=JobPriority.NORMAL,
    )
    actors.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()
