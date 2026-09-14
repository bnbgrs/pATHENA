"""Registration boundary for durable Deep backup verification jobs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from athena.jobs.backup_verify_payload import (
    BACKUP_VERIFY_DEEP_JOB_TYPE,
    BackupDeepVerifyPayload,
    BackupDeepVerifyPayloadError,
    validate_backup_deep_verify_payload,
)


class BackupDeepVerifyRegistrationError(ValueError):
    """Raised when create-time Deep-verify registration input is unsafe."""


@dataclass(frozen=True, slots=True)
class BackupDeepVerifyRegistration:
    """Immutable registration contract for the durable Deep-verify job type."""

    job_type: str = BACKUP_VERIFY_DEEP_JOB_TYPE
    control_lane_safe: bool = True
    retry_via_backup_create: bool = False

    def validate_create_payload(
        self,
        *,
        requested_scope: Mapping[str, Any] | None,
        pinned_configuration: Mapping[str, Any] | None,
    ) -> BackupDeepVerifyPayload:
        """Validate the exact persistent payload before a durable write."""
        try:
            return validate_backup_deep_verify_payload(
                requested_scope=requested_scope,
                pinned_configuration=pinned_configuration,
            )
        except BackupDeepVerifyPayloadError as exc:
            raise BackupDeepVerifyRegistrationError(str(exc)) from exc


BACKUP_VERIFY_DEEP_REGISTRATION = BackupDeepVerifyRegistration()
BACKUP_VERIFY_DEEP_BUILTIN_JOB_TYPES = frozenset({BACKUP_VERIFY_DEEP_JOB_TYPE})
