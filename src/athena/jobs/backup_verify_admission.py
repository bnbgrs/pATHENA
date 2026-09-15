"""Fail-closed admission boundary for durable Deep backup verification occurrences."""

from __future__ import annotations

from dataclasses import dataclass

from athena.jobs.backup_verify_occurrence import BackupDeepVerifyOccurrence
from athena.jobs.backup_verify_registration import BACKUP_VERIFY_DEEP_REGISTRATION


class BackupDeepVerifyAdmissionError(ValueError):
    """Raised when a materialized Deep-verify occurrence is unsafe to persist."""


@dataclass(frozen=True, slots=True)
class BackupDeepVerifyCreateRequest:
    """Canonical service-facing inputs for one durable Deep-verify job."""

    job_type: str
    requested_scope: dict[str, object]
    pinned_configuration: dict[str, object]
    next_run_at_us: int
    idempotency_key: str


def admit_backup_deep_verify_occurrence(
    occurrence: BackupDeepVerifyOccurrence,
) -> BackupDeepVerifyCreateRequest:
    """Revalidate one occurrence before it may cross the durable-write boundary."""
    if not isinstance(occurrence, BackupDeepVerifyOccurrence):
        raise TypeError("occurrence must be a BackupDeepVerifyOccurrence.")
    registration = BACKUP_VERIFY_DEEP_REGISTRATION
    if occurrence.job_type != registration.job_type:
        raise BackupDeepVerifyAdmissionError("Deep-verify occurrence job type changed.")
    if registration.control_lane_safe is not True:
        raise BackupDeepVerifyAdmissionError("Deep-verify job is not CONTROL-lane safe.")
    if registration.retry_via_backup_create is not False:
        raise BackupDeepVerifyAdmissionError(
            "Deep-verify admission must never retry through backup.create."
        )

    try:
        validated = registration.validate_create_payload(
            requested_scope=occurrence.requested_scope,
            pinned_configuration=occurrence.pinned_configuration,
        )
    except ValueError as exc:
        raise BackupDeepVerifyAdmissionError(str(exc)) from exc

    if validated.snapshot_id != occurrence.snapshot_id:
        raise BackupDeepVerifyAdmissionError("Deep-verify snapshot identity changed.")
    if validated.occurrence_slot_us != occurrence.occurrence_slot_us:
        raise BackupDeepVerifyAdmissionError("Deep-verify occurrence slot changed.")

    expected_idempotency_key = (
        f"{registration.job_type}:{validated.snapshot_id}:"
        f"{validated.occurrence_slot_us}"
    )
    if occurrence.idempotency_key != expected_idempotency_key:
        raise BackupDeepVerifyAdmissionError("Deep-verify idempotency identity changed.")

    return BackupDeepVerifyCreateRequest(
        job_type=registration.job_type,
        requested_scope=dict(validated.requested_scope),
        pinned_configuration=dict(validated.pinned_configuration),
        next_run_at_us=validated.occurrence_slot_us,
        idempotency_key=expected_idempotency_key,
    )
