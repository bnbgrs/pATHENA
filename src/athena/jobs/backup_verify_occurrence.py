"""Side-effect-free materialization for periodic durable Deep-verify occurrences."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.jobs.backup_verify_payload import build_backup_deep_verify_payload
from athena.jobs.backup_verify_registration import BACKUP_VERIFY_DEEP_REGISTRATION


class BackupDeepVerifyOccurrenceError(ValueError):
    """Raised when a planned Deep-verify occurrence cannot be materialized safely."""


@dataclass(frozen=True, slots=True)
class BackupDeepVerifyOccurrence:
    """Canonical durable-job inputs for one planned Deep verification occurrence."""

    job_type: str
    snapshot_id: uuid.UUID
    occurrence_slot_us: int
    idempotency_key: str
    requested_scope: dict[str, object]
    pinned_configuration: dict[str, object]


def materialize_backup_deep_verify_occurrence(
    *,
    snapshot_id: uuid.UUID,
    occurrence_slot_us: int,
) -> BackupDeepVerifyOccurrence:
    """Build exact durable inputs without writing a job or creating a backup."""
    try:
        payload = build_backup_deep_verify_payload(
            snapshot_id=snapshot_id,
            occurrence_slot_us=occurrence_slot_us,
        )
        validated = BACKUP_VERIFY_DEEP_REGISTRATION.validate_create_payload(
            requested_scope=payload.requested_scope,
            pinned_configuration=payload.pinned_configuration,
        )
    except (TypeError, ValueError) as exc:
        raise BackupDeepVerifyOccurrenceError(str(exc)) from exc

    if validated != payload:
        raise BackupDeepVerifyOccurrenceError(
            "Deep-verify registration changed the canonical occurrence payload."
        )

    return BackupDeepVerifyOccurrence(
        job_type=BACKUP_VERIFY_DEEP_REGISTRATION.job_type,
        snapshot_id=validated.snapshot_id,
        occurrence_slot_us=validated.occurrence_slot_us,
        idempotency_key=(
            f"{BACKUP_VERIFY_DEEP_REGISTRATION.job_type}:"
            f"{validated.snapshot_id}:{validated.occurrence_slot_us}"
        ),
        requested_scope=validated.requested_scope,
        pinned_configuration=validated.pinned_configuration,
    )
