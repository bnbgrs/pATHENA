from __future__ import annotations

from unittest.mock import Mock

import pytest

from athena.jobs.backup_verify_durable_service import BackupDeepVerifyDurableJobService
from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.models import JobPriority
from athena.jobs.service import InvalidJobPayloadError


def _valid_payload() -> tuple[dict[str, object], dict[str, object]]:
    return (
        {"snapshot_id": "snapshot-1", "occurrence_slot_us": 1},
        {"pipeline_version": "backup-deep-verify-v1"},
    )


def test_deep_verify_rejects_invalid_payload_before_actor_or_repository_write() -> None:
    repository = Mock()
    chat = Mock()
    service = BackupDeepVerifyDurableJobService(repository, chat)

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            requested_scope={"snapshot_id": "snapshot-1"},
            pinned_configuration={"pipeline_version": "backup-deep-verify-v1"},
        )

    chat.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()


def test_deep_verify_persists_validated_payload_once() -> None:
    repository = Mock()
    repository.create.return_value = Mock()
    chat = Mock()
    chat.ensure_local_user.return_value = "local-user"
    service = BackupDeepVerifyDurableJobService(repository, chat)
    scope, configuration = _valid_payload()

    result = service.create(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        priority=JobPriority.TIME_CRITICAL,
        requested_scope=scope,
        pinned_configuration=configuration,
        next_run_at_us=2,
    )

    assert result is repository.create.return_value
    chat.ensure_local_user.assert_called_once_with()
    repository.create.assert_called_once()
    call = repository.create.call_args.kwargs
    assert call["job_type"] == BACKUP_VERIFY_DEEP_JOB_TYPE
    assert call["actor_id"] == "local-user"
    assert call["priority"] is JobPriority.TIME_CRITICAL
    assert call["next_run_at_us"] == 2
    assert '"snapshot_id":"snapshot-1"' in call["requested_scope_json"]
    assert '"occurrence_slot_us":1' in call["requested_scope_json"]
    assert call["pinned_configuration_json"] == '{"pipeline_version":"backup-deep-verify-v1"}'


def test_non_deep_verify_job_delegates_to_canonical_service_validation() -> None:
    repository = Mock()
    repository.create.return_value = Mock()
    chat = Mock()
    chat.ensure_local_user.return_value = "local-user"
    service = BackupDeepVerifyDurableJobService(repository, chat)

    service.create(job_type="backup.create")

    chat.ensure_local_user.assert_called_once_with()
    repository.create.assert_called_once()
