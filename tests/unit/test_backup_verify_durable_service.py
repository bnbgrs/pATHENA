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
        submit=submit or Mock(return_value="job-1"),
    )


def test_submit_occurrence_uses_stable_idempotency_key() -> None:
    submit = Mock(return_value="job-1")
    service = _service(submit=submit)

    payload, inputs = _valid_payload()
    first = service.submit_occurrence(payload=payload, inputs=inputs)
    second = service.submit_occurrence(payload=payload, inputs=inputs)

    assert first == "job-1"
    assert second == "job-1"
    assert submit.call_count == 2
    first_call = submit.call_args_list[0].kwargs
    second_call = submit.call_args_list[1].kwargs
    assert first_call["job_type"] == BACKUP_VERIFY_DEEP_JOB_TYPE
    assert first_call["priority"] == JobPriority.CONTROL
    assert first_call["payload"] == payload
    assert first_call["inputs"] == inputs
    assert first_call["idempotency_key"] == second_call["idempotency_key"]
    assert first_call["idempotency_key"].startswith("backup-verify-deep:")


def test_submit_occurrence_rejects_invalid_payload_before_submission() -> None:
    submit = Mock(return_value="job-1")
    service = _service(submit=submit)

    payload, inputs = _valid_payload()
    payload["snapshot_id"] = "not-a-uuid"

    with pytest.raises(InvalidJobPayloadError):
        service.submit_occurrence(payload=payload, inputs=inputs)

    submit.assert_not_called()


def test_submit_occurrence_rejects_invalid_inputs_before_submission() -> None:
    submit = Mock(return_value="job-1")
    service = _service(submit=submit)

    payload, inputs = _valid_payload()
    inputs["pipeline_version"] = "unexpected"

    with pytest.raises(InvalidJobPayloadError):
        service.submit_occurrence(payload=payload, inputs=inputs)

    submit.assert_not_called()
