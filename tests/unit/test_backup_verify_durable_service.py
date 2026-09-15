from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from athena.jobs.backup_verify_durable_service import (
    BackupDeepVerifyDurableJobService,
)
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


def _service() -> tuple[BackupDeepVerifyDurableJobService, Mock, Mock]:
    repository = Mock()
    chat = Mock()
    service = BackupDeepVerifyDurableJobService(repository=repository, chat=chat)
    return service, repository, chat


def test_deep_verify_rejects_malformed_payload_before_side_effects() -> None:
    service, repository, chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            requested_scope={"snapshot_id": "not-a-uuid", "occurrence_slot_us": 1},
            pinned_configuration={"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION},
            priority=JobPriority.TIME_CRITICAL,
        )

    chat.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()


def test_deep_verify_persists_validated_payload_once() -> None:
    requested_scope, pinned_configuration = _valid_payload()
    service, repository, chat = _service()
    repository.create.return_value = "job-1"
    chat.ensure_local_user.return_value = "actor-1"

    result = service.create(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        requested_scope=requested_scope,
        pinned_configuration=pinned_configuration,
        priority=JobPriority.TIME_CRITICAL,
    )

    assert result == "job-1"
    chat.ensure_local_user.assert_called_once_with()
    repository.create.assert_called_once_with(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        actor_id="actor-1",
        priority=JobPriority.TIME_CRITICAL,
        requested_scope_json=json.dumps(
            requested_scope,
            sort_keys=True,
            separators=(",", ":"),
        ),
        pinned_configuration_json=json.dumps(
            pinned_configuration,
            sort_keys=True,
            separators=(",", ":"),
        ),
        next_run_at_us=None,
    )


def test_non_deep_verify_job_delegates_to_canonical_service_validation() -> None:
    service, repository, chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type="backup.create",
            requested_scope={},
            priority=JobPriority.NORMAL,
        )

    chat.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()
