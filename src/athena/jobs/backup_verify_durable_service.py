"""DurableJobService integration for periodic Deep backup verification."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.backup_verify_service_boundary import (
    BackupDeepVerifyServiceBoundaryError,
    validate_backup_deep_verify_service_create,
)
from athena.jobs.models import JobPriority, JobRecord
from athena.jobs.service import DurableJobService, InvalidJobPayloadError


class BackupDeepVerifyDurableJobService(DurableJobService):
    """Durable job service that admits the fail-closed Deep-verify job contract."""

    BUILTIN_JOB_TYPES = DurableJobService.BUILTIN_JOB_TYPES | {BACKUP_VERIFY_DEEP_JOB_TYPE}

    def create(
        self,
        *,
        job_type: str,
        priority: JobPriority = JobPriority.NORMAL,
        requested_scope: Mapping[str, Any] | None = None,
        pinned_configuration: Mapping[str, Any] | None = None,
        next_run_at_us: int | None = None,
    ) -> JobRecord:
        if job_type != BACKUP_VERIFY_DEEP_JOB_TYPE:
            return super().create(
                job_type=job_type,
                priority=priority,
                requested_scope=requested_scope,
                pinned_configuration=pinned_configuration,
                next_run_at_us=next_run_at_us,
            )

        try:
            validated = validate_backup_deep_verify_service_create(
                job_type=job_type,
                requested_scope=requested_scope,
                pinned_configuration=pinned_configuration,
            )
        except BackupDeepVerifyServiceBoundaryError as exc:
            raise InvalidJobPayloadError(str(exc)) from exc

        # The strict Deep-verify boundary has already normalized and validated the
        # payload. Persist through the canonical DurableJobService machinery by
        # temporarily dispatching only its serialization/persistence tail; no
        # backup.create path is involved.
        normalized_job_type = self._registered_job_type(job_type)
        from athena.jobs.service import (
            _canonical_json,
            _job_priority,
            _optional_nonnegative_int,
        )

        _job_priority(priority)
        _optional_nonnegative_int(next_run_at_us, "next_run_at_us")
        requested_scope_json = _canonical_json(validated.requested_scope)
        pinned_configuration_json = _canonical_json(validated.pinned_configuration)
        actor_id = self.chat.ensure_local_user()
        return self.repository.create(
            job_type=normalized_job_type,
            actor_id=actor_id,
            priority=priority,
            requested_scope_json=requested_scope_json,
            pinned_configuration_json=pinned_configuration_json,
            next_run_at_us=next_run_at_us,
        )
