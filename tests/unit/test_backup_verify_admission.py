from __future__ import annotations

import uuid

import pytest

from athena.jobs.backup_verify_admission import (
    BackupDeepVerifyAdmissionError,
    admit_backup_deep_verify_occurrence,
)
from athena.jobs.backup_verify_occurrence import BackupDeepVerifyOccurrence
from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_PIPELINE_VERSION


def _occurrence() -> BackupDeepVerifyOccurrence:
    snapshot_id = uuid.uuid4()
    slot = 123_000_000
    return BackupDeepVerifyOccurrence(
        job_type="backup.verify_deep",
        snapshot_id=snapshot_id,
        occurrence_slot_us=slot,
        idempotency_key=f"backup.verify_deep:{snapshot_id}:{slot}",
        requested_scope={
            "snapshot_id": str(snapshot_id),
            "occurrence_slot_us": slot,
        },
        pinned_configuration={
            "pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
        },
    )


def test_admission_returns_exact_service_facing_inputs() -> None:
    occurrence = _occurrence()

    admitted = admit_backup_deep_verify_occurrence(occurrence)

    assert admitted.job_type == "backup.verify_deep"
    assert admitted.requested_scope == occurrence.requested_scope
    assert admitted.pinned_configuration == occurrence.pinned_configuration
    assert admitted.next_run_at_us == occurrence.occurrence_slot_us
    assert admitted.idempotency_key == occurrence.idempotency_key


def test_admission_rejects_wrong_job_type() -> None:
    occurrence = _occurrence()
    changed = BackupDeepVerifyOccurrence(
        job_type="backup.create",
        snapshot_id=occurrence.snapshot_id,
        occurrence_slot_us=occurrence.occurrence_slot_us,
        idempotency_key=occurrence.idempotency_key,
        requested_scope=occurrence.requested_scope,
        pinned_configuration=occurrence.pinned_configuration,
    )

    with pytest.raises(BackupDeepVerifyAdmissionError, match="job type changed"):
        admit_backup_deep_verify_occurrence(changed)


def test_admission_rejects_changed_idempotency_identity() -> None:
    occurrence = _occurrence()
    changed = BackupDeepVerifyOccurrence(
        job_type=occurrence.job_type,
        snapshot_id=occurrence.snapshot_id,
        occurrence_slot_us=occurrence.occurrence_slot_us,
        idempotency_key="backup.verify_deep:wrong:identity",
        requested_scope=occurrence.requested_scope,
        pinned_configuration=occurrence.pinned_configuration,
    )

    with pytest.raises(BackupDeepVerifyAdmissionError, match="idempotency identity changed"):
        admit_backup_deep_verify_occurrence(changed)


def test_admission_rejects_payload_snapshot_drift() -> None:
    occurrence = _occurrence()
    changed = BackupDeepVerifyOccurrence(
        job_type=occurrence.job_type,
        snapshot_id=occurrence.snapshot_id,
        occurrence_slot_us=occurrence.occurrence_slot_us,
        idempotency_key=occurrence.idempotency_key,
        requested_scope={
            "snapshot_id": str(uuid.uuid4()),
            "occurrence_slot_us": occurrence.occurrence_slot_us,
        },
        pinned_configuration=occurrence.pinned_configuration,
    )

    with pytest.raises(BackupDeepVerifyAdmissionError, match="snapshot identity changed"):
        admit_backup_deep_verify_occurrence(changed)


def test_admission_rejects_payload_slot_drift() -> None:
    occurrence = _occurrence()
    changed = BackupDeepVerifyOccurrence(
        job_type=occurrence.job_type,
        snapshot_id=occurrence.snapshot_id,
        occurrence_slot_us=occurrence.occurrence_slot_us,
        idempotency_key=occurrence.idempotency_key,
        requested_scope={
            "snapshot_id": str(occurrence.snapshot_id),
            "occurrence_slot_us": occurrence.occurrence_slot_us + 1,
        },
        pinned_configuration=occurrence.pinned_configuration,
    )

    with pytest.raises(BackupDeepVerifyAdmissionError, match="occurrence slot changed"):
        admit_backup_deep_verify_occurrence(changed)


def test_admission_rejects_wrong_pipeline_version() -> None:
    occurrence = _occurrence()
    changed = BackupDeepVerifyOccurrence(
        job_type=occurrence.job_type,
        snapshot_id=occurrence.snapshot_id,
        occurrence_slot_us=occurrence.occurrence_slot_us,
        idempotency_key=occurrence.idempotency_key,
        requested_scope=occurrence.requested_scope,
        pinned_configuration={"pipeline_version": "wrong"},
    )

    with pytest.raises(BackupDeepVerifyAdmissionError):
        admit_backup_deep_verify_occurrence(changed)
