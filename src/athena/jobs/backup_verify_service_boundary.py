"""DurableJobService-facing validation boundary for Deep backup verification."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.backup_verify_registration import (
    BACKUP_VERIFY_DEEP_REGISTRATION,
    BackupDeepVerifyRegistrationError,
)


class BackupDeepVerifyServiceBoundaryError(ValueError):
    """Raised when a Deep-verify create request must fail before persistence."""


@dataclass(frozen=True, slots=True)
class ValidatedBackupDeepVerifyCreate:
    """Normalized service-facing Deep-verify payload safe for durable persistence."""

    requested_scope: Mapping[str, Any]
    pinned_configuration: Mapping[str, Any]


def validate_backup_deep_verify_service_create(
    *,
    job_type: str,
    requested_scope: Mapping[str, Any] | None,
    pinned_configuration: Mapping[str, Any] | None,
) -> ValidatedBackupDeepVerifyCreate:
    """Fail closed before actor or repository side effects for Deep verification."""
    if job_type != BACKUP_VERIFY_DEEP_JOB_TYPE:
        raise BackupDeepVerifyServiceBoundaryError(
            f"Expected job type {BACKUP_VERIFY_DEEP_JOB_TYPE!r}."
        )
    if BACKUP_VERIFY_DEEP_REGISTRATION.control_lane_safe is not True:
        raise BackupDeepVerifyServiceBoundaryError(
            "Deep-verify registration must remain CONTROL-lane safe."
        )
    if BACKUP_VERIFY_DEEP_REGISTRATION.retry_via_backup_create is not False:
        raise BackupDeepVerifyServiceBoundaryError(
            "Deep-verify retries must never route through backup.create."
        )
    try:
        payload = BACKUP_VERIFY_DEEP_REGISTRATION.validate_create_payload(
            requested_scope=requested_scope,
            pinned_configuration=pinned_configuration,
        )
    except BackupDeepVerifyRegistrationError as exc:
        raise BackupDeepVerifyServiceBoundaryError(str(exc)) from exc

    return ValidatedBackupDeepVerifyCreate(
        requested_scope=payload.requested_scope,
        pinned_configuration=payload.pinned_configuration,
    )
