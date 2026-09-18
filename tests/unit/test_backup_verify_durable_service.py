from __future__ import annotations

from unittest.mock import Mock

import pytest

import athena.jobs.backup_verify_durable_service as durable_service
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
    chat = Mock()
    chat.ensure_local_user.return_value = "actor-1"
    service = durable_service.BackupDeepVerifyDurableJobService(repository, chat)
    requested_scope, pinned_configuration = _valid_payload()

    service.create(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        priority=JobPriority.MAINTENANCE,
        requested_scope=requested_scope,
        pinned_configuration=pinned_configuration,
        next_run_at_us=123,
    )

    chat.ensure_local_user.assert_called_once_with()
    repository.create.assert_called_once_with(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        actor_id="actor-1",
        priority=JobPriority.MAINTENANCE,
        requested_scope_json=(
            '{"occurrence_slot_us":1,'
            '"snapshot_id":"12345678-1234-5678-9234-567812345678"}'
        ),
        pinned_configuration_json=(
            '{"pipeline_version":"backup-deep-verify-v1"}'
        ),
        next_run_at_us=123,
    )


def test_create_rejects_invalid_snapshot_id_before_persist() -> None:
    repository = Mock()
    chat = Mock()
    service = durable_service.BackupDeepVerifyDurableJobService(repository, chat)
    requested_scope, pinned_configuration = _valid_payload()
    requested_scope["snapshot_id"] = "not-a-uuid"

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            priority=JobPriority.MAINTENANCE,
            requested_scope=requested_scope,
            pinned_configuration=pinned_configuration,
            next_run_at_us=123,
        )

    chat.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()


def test_create_rejects_wrong_pipeline_version_before_persist() -> None:
    repository = Mock()
    chat = Mock()
    service = durable_service.BackupDeepVerifyDurableJobService(repository, chat)
    requested_scope, pinned_configuration = _valid_payload()
    pinned_configuration["pipeline_version"] = "wrong"

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
            priority=JobPriority.MAINTENANCE,
            requested_scope=requested_scope,
            pinned_configuration=pinned_configuration,
            next_run_at_us=123,
        )

    chat.ensure_local_user.assert_not_called()
    repository.create.assert_not_called()
