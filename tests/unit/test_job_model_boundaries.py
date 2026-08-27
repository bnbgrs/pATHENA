from __future__ import annotations

import uuid

import pytest

from athena.jobs.models import CheckpointRecord, JobPriority, JobRecord, JobState


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _job(**overrides: object) -> JobRecord:
    values: dict[str, object] = {
        "job_id": _uuid(),
        "job_type": "research",
        "created_at_us": 10,
        "created_by_actor_id": _uuid(),
        "priority": JobPriority.NORMAL,
        "state": JobState.QUEUED,
        "requested_scope_json": '{"scope":"all"}',
        "processing_run_id": None,
        "current_stage": None,
        "last_checkpoint_id": None,
        "retry_count": 0,
        "next_run_at_us": None,
        "blocked_reason": None,
        "pinned_configuration_json": "{}",
        "protection_scope_id": None,
        "protected_payload_id": None,
        "worker_id": None,
        "lease_token": None,
        "lease_acquired_at_us": None,
        "lease_expires_at_us": None,
        "heartbeat_at_us": None,
        "fencing_sequence": 0,
        "updated_at_us": 10,
    }
    values.update(overrides)
    return JobRecord(**values)  # type: ignore[arg-type]


def _checkpoint(**overrides: object) -> CheckpointRecord:
    values: dict[str, object] = {
        "checkpoint_id": _uuid(),
        "job_id": _uuid(),
        "processing_stage_id": None,
        "created_at_us": 10,
        "progress_state_json": "{}",
        "last_confirmed_input_json": None,
        "last_confirmed_output_json": None,
        "resume_metadata_json": None,
        "commit_id": None,
        "protection_scope_id": None,
        "protected_payload_id": None,
        "fencing_sequence": 0,
    }
    values.update(overrides)
    return CheckpointRecord(**values)  # type: ignore[arg-type]


def test_job_record_accepts_valid_minimal_record() -> None:
    assert _job().state is JobState.QUEUED


@pytest.mark.parametrize("value", [True, False, 1.5, "1", None])
def test_job_record_rejects_non_integer_retry_count(value: object) -> None:
    with pytest.raises(TypeError, match="retry_count must be an integer"):
        _job(retry_count=value)


def test_job_record_rejects_invalid_requested_scope_json() -> None:
    with pytest.raises(ValueError, match="requested_scope_json must contain strict JSON"):
        _job(requested_scope_json="{")


def test_job_record_rejects_blank_job_type() -> None:
    with pytest.raises(ValueError, match="job_type must use canonical trimmed text"):
        _job(job_type="   ")


def test_job_record_rejects_empty_lease_token() -> None:
    with pytest.raises(ValueError, match="lease_token must not be empty"):
        _job(lease_token=b"")


def test_job_record_rejects_reversed_lease_window() -> None:
    with pytest.raises(ValueError, match="lease_expires_at_us precedes"):
        _job(lease_acquired_at_us=20, lease_expires_at_us=19)


def test_job_record_rejects_updated_before_created() -> None:
    with pytest.raises(ValueError, match="updated_at_us precedes"):
        _job(created_at_us=11, updated_at_us=10)


def test_checkpoint_accepts_valid_json_payloads() -> None:
    assert _checkpoint(resume_metadata_json='{"cursor":1}').fencing_sequence == 0


@pytest.mark.parametrize("value", [True, False, 1.5, "1", None])
def test_checkpoint_rejects_non_integer_fencing_sequence(value: object) -> None:
    with pytest.raises(TypeError, match="fencing_sequence must be an integer"):
        _checkpoint(fencing_sequence=value)


def test_checkpoint_rejects_invalid_progress_json() -> None:
    with pytest.raises(ValueError, match="progress_state_json must contain strict JSON"):
        _checkpoint(progress_state_json="[")


def test_checkpoint_rejects_non_uuid_job_id() -> None:
    with pytest.raises(TypeError, match="job_id must be a UUID"):
        _checkpoint(job_id="not-a-uuid")
