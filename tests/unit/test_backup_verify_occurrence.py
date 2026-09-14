import uuid

import pytest

from athena.jobs.backup_verify_occurrence import (
    BackupDeepVerifyOccurrenceError,
    materialize_backup_deep_verify_occurrence,
)
from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_PIPELINE_VERSION


def test_materializes_exact_durable_inputs() -> None:
    snapshot_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    occurrence = materialize_backup_deep_verify_occurrence(
        snapshot_id=snapshot_id,
        occurrence_slot_us=42,
    )

    assert occurrence.job_type == "backup.verify_deep"
    assert occurrence.snapshot_id == snapshot_id
    assert occurrence.occurrence_slot_us == 42
    assert occurrence.idempotency_key == f"backup.verify_deep:{snapshot_id}:42"
    assert occurrence.requested_scope == {
        "snapshot_id": str(snapshot_id),
        "occurrence_slot_us": 42,
    }
    assert occurrence.pinned_configuration == {
        "pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
    }


def test_same_occurrence_is_deterministic() -> None:
    snapshot_id = uuid.uuid4()
    first = materialize_backup_deep_verify_occurrence(
        snapshot_id=snapshot_id,
        occurrence_slot_us=7,
    )
    second = materialize_backup_deep_verify_occurrence(
        snapshot_id=snapshot_id,
        occurrence_slot_us=7,
    )
    assert first == second


def test_distinct_slots_have_distinct_idempotency_keys() -> None:
    snapshot_id = uuid.uuid4()
    first = materialize_backup_deep_verify_occurrence(
        snapshot_id=snapshot_id,
        occurrence_slot_us=7,
    )
    second = materialize_backup_deep_verify_occurrence(
        snapshot_id=snapshot_id,
        occurrence_slot_us=8,
    )
    assert first.idempotency_key != second.idempotency_key


@pytest.mark.parametrize("bad", [-1, True, 1.5, "1", None])
def test_rejects_invalid_occurrence_slot(bad: object) -> None:
    with pytest.raises(BackupDeepVerifyOccurrenceError):
        materialize_backup_deep_verify_occurrence(
            snapshot_id=uuid.uuid4(),
            occurrence_slot_us=bad,  # type: ignore[arg-type]
        )


def test_rejects_non_uuid_snapshot() -> None:
    with pytest.raises(BackupDeepVerifyOccurrenceError):
        materialize_backup_deep_verify_occurrence(
            snapshot_id="123",  # type: ignore[arg-type]
            occurrence_slot_us=0,
        )
