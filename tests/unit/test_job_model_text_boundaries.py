from __future__ import annotations

import uuid

import pytest

from athena.jobs.models import JobPriority, JobRecord, JobState


def _record(**overrides: object) -> JobRecord:
    values: dict[str, object] = {
        "job_id": uuid.uuid4(),
        "job_type": "source.process",
        "created_at_us": 10,
        "created_by_actor_id": uuid.uuid4(),
        "priority": JobPriority.NORMAL,
        "state": JobState.QUEUED,
        "requested_scope_json": None,
        "processing_run_id": None,
        "current_stage": None,
        "last_checkpoint_id": None,
        "retry_count": 0,
        "next_run_at_us": None,
        "blocked_reason": None,
        "pinned_configuration_json": None,
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


@pytest.mark.parametrize("job_type", ["", " ", " source.process", "source.process "])
def test_job_record_rejects_noncanonical_job_type(job_type: str) -> None:
    with pytest.raises(ValueError):
        _record(job_type=job_type)


@pytest.mark.parametrize("field", ["current_stage", "blocked_reason", "worker_id"])
@pytest.mark.parametrize("value", ["", " ", " value", "value "])
def test_job_record_rejects_noncanonical_optional_text(field: str, value: str) -> None:
    with pytest.raises(ValueError):
        _record(**{field: value})


def test_job_record_accepts_canonical_machine_text() -> None:
    record = _record(
        job_type="backup.create",
        current_stage="copy",
        blocked_reason="waiting_storage",
        worker_id="worker-1",
    )

    assert record.job_type == "backup.create"
    assert record.current_stage == "copy"
    assert record.blocked_reason == "waiting_storage"
    assert record.worker_id == "worker-1"
