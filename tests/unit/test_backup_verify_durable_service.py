from __future__ import annotations

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


def test_create_persists_maintenance_job() -> None:
    repository = Mock()
    chat = Mock()
    chat.resolve_or_create_thread_for_actor.return_value = "thread-1"
    service = BackupDeepVerifyDurableJobService(repository, chat)
    payload, version = _valid_payload()

    service.create(
        actor_id="actor-1",
        payload=payload,
        version=version,
        next_run_at_us=123,
    )

    repository.create.assert_called_once()
    job = repository.create.call_args.args[0]
    assert job.job_type == BACKUP_VERIFY_DEEP_JOB_TYPE
    assert job.priority is JobPriority.MAINTENANCE
    assert job.actor_id == "actor-1"
    assert job.next_run_at_us == 123
    assert job.payload == payload
    assert job.version == version


def test_create_rejects_invalid_snapshot_id_before_persist() -> None:
    repository = Mock()
    chat = Mock()
    service = BackupDeepVerifyDurableJobService(repository, chat)
    payload, version = _valid_payload()
    payload["snapshot_id"] = "not-a-uuid"

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            actor_id="actor-1",
            payload=payload,
            version=version,
            next_run_at_us=123,
        )

    repository.create.assert_not_called()


def test_create_rejects_wrong_pipeline_version_before_persist() -> None:
    repository = Mock()
    chat = Mock()
    service = BackupDeepVerifyDurableJobService(repository, chat)
    payload, version = _valid_payload()
    version["pipeline_version"] = "wrong"

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            actor_id="actor-1",
            payload=payload,
            version=version,
            next_run_at_us=123,
        )

    repository.create.assert_not_called()
