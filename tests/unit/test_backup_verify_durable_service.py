from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

import athena.jobs.backup_verify_durable_service as backup_verify_durable_service
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
    submit: Mock | None = None,
) -> backup_verify_durable_service.BackupDeepVerifyDurableJobService:
    return backup_verify_durable_service.BackupDeepVerifyDurableJobService(
        submit_job=submit or Mock(return_value="job-1")
    )


def test_submit_occurrence_uses_durable_backup_verify_job_contract() -> None:
    submit = Mock(return_value="job-42")
    service = _service(submit=submit)
    payload, input_snapshot = _valid_payload()

    job_id = service.submit_occurrence(payload=payload, input_snapshot=input_snapshot)

    assert job_id == "job-42"
    submit.assert_called_once_with(
        BACKUP_VERIFY_DEEP_JOB_TYPE,
        payload=payload,
        priority=JobPriority.LOW,
        input_snapshot=input_snapshot,
    )


def test_submit_occurrence_rejects_invalid_payload_before_admission() -> None:
    submit = Mock(return_value="job-42")
    service = _service(submit=submit)
    payload, input_snapshot = _valid_payload()
    payload["snapshot_id"] = "relative/path"

    with pytest.raises(InvalidJobPayloadError, match="snapshot_id"):
        service.submit_occurrence(payload=payload, input_snapshot=input_snapshot)

    submit.assert_not_called()


def test_submit_occurrence_rejects_invalid_input_snapshot_before_admission() -> None:
    submit = Mock(return_value="job-42")
    service = _service(submit=submit)
    payload, input_snapshot = _valid_payload()
    input_snapshot["pipeline_version"] = "wrong"

    with pytest.raises(InvalidJobPayloadError, match="pipeline_version"):
        service.submit_occurrence(payload=payload, input_snapshot=input_snapshot)

    submit.assert_not_called()
