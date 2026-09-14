"""Durable execution worker for periodic Deep backup verification."""

from __future__ import annotations

import json

from athena.backup.service import BackupRestoreError, BackupService
from athena.backup.target_lock import BackupTargetBusyError
from athena.common.time import utc_now_us
from athena.jobs.backup_verify_payload import (
    BACKUP_VERIFY_DEEP_JOB_TYPE,
    BackupDeepVerifyPayload,
    BackupDeepVerifyPayloadError,
    validate_backup_deep_verify_payload,
)
from athena.jobs.models import JobRecord, JobState, WaitingReason
from athena.jobs.service import DurableJobService

_DEFAULT_RETRY_SECONDS = 5 * 60
_DEFAULT_LEASE_EXTENSION_SECONDS = 15 * 60


class BackupDeepVerifyJobError(RuntimeError):
    """Raised when one durable Deep verification job cannot continue safely."""


def _positive_seconds(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be an integer >= 1.")
    return value


class DurableBackupDeepVerifyWorker:
    """Execute one existing restore point's Deep verification durably."""

    def __init__(
        self,
        *,
        jobs: DurableJobService,
        backup: BackupService,
        retry_seconds: int = _DEFAULT_RETRY_SECONDS,
        lease_extension_seconds: int = _DEFAULT_LEASE_EXTENSION_SECONDS,
    ) -> None:
        self.retry_seconds = _positive_seconds(
            retry_seconds,
            label="Backup Deep verify retry_seconds",
        )
        self.lease_extension_seconds = _positive_seconds(
            lease_extension_seconds,
            label="Backup Deep verify lease_extension_seconds",
        )
        self.jobs = jobs
        self.backup = backup

    def process_leased(self, job: JobRecord) -> JobRecord:
        """Verify one persisted snapshot without creating or replacing a backup."""
        if job.job_type != BACKUP_VERIFY_DEEP_JOB_TYPE:
            raise BackupDeepVerifyJobError(
                f"Unexpected Deep verify job type {job.job_type!r}."
            )
        lease_token = job.lease_token
        if lease_token is None:
            raise BackupDeepVerifyJobError(
                f"Deep verify job {job.job_id} has no live lease token."
            )
        if job.state is JobState.CANCEL_REQUESTED:
            return self.jobs.acknowledge_cancel(
                job.job_id,
                lease_token=lease_token,
            )
        if job.state is not JobState.RUNNING:
            raise BackupDeepVerifyJobError(
                f"Deep verify job {job.job_id} is not running."
            )

        payload = self._payload(job)
        snapshot_id = payload.snapshot_id
        try:
            snapshot = self.backup.get_snapshot(snapshot_id)
            target = self.backup.target_status(snapshot.target_id)
        except BackupTargetBusyError:
            return self._wait(
                job,
                lease_token=lease_token,
                reason=WaitingReason.BACKOFF,
            )
        except OSError:
            return self._wait(
                job,
                lease_token=lease_token,
                reason=WaitingReason.STORAGE,
            )
        except BackupRestoreError as exc:
            raise BackupDeepVerifyJobError(
                f"Deep verify snapshot {snapshot_id} failed identity validation."
            ) from exc

        if target.status != "active":
            return self._wait(
                job,
                lease_token=lease_token,
                reason=WaitingReason.STORAGE,
            )

        self.jobs.heartbeat(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=self.lease_extension_seconds,
        )
        try:
            verified = self.backup.verify_deep(snapshot_id)
        except BackupTargetBusyError:
            return self._wait(
                job,
                lease_token=lease_token,
                reason=WaitingReason.BACKOFF,
            )
        except OSError:
            return self._wait(
                job,
                lease_token=lease_token,
                reason=WaitingReason.STORAGE,
            )
        except BackupRestoreError as exc:
            try:
                refreshed = self.backup.target_status(snapshot.target_id)
            except (BackupTargetBusyError, OSError):
                return self._wait(
                    job,
                    lease_token=lease_token,
                    reason=WaitingReason.STORAGE,
                )
            except BackupRestoreError:
                refreshed = None
            if refreshed is not None and refreshed.status != "active":
                return self._wait(
                    job,
                    lease_token=lease_token,
                    reason=WaitingReason.STORAGE,
                )
            raise BackupDeepVerifyJobError(
                f"Deep verification for snapshot {snapshot_id} failed safely."
            ) from exc

        self.jobs.checkpoint(
            job.job_id,
            lease_token=lease_token,
            current_stage="backup_deep_verify_complete",
            progress_state={
                "snapshot_id": str(snapshot_id),
                "occurrence_slot_us": payload.occurrence_slot_us,
                "target_id": str(verified.target_id),
                "verification_status": verified.verification_status,
            },
            last_confirmed_output={
                "snapshot_id": str(snapshot_id),
                "occurrence_slot_us": payload.occurrence_slot_us,
                "verification_status": verified.verification_status,
            },
        )
        return self.jobs.complete(
            job.job_id,
            lease_token=lease_token,
        )

    def _payload(self, job: JobRecord) -> BackupDeepVerifyPayload:
        requested_scope = self._json_object(
            job.requested_scope_json,
            label="requested scope",
            job_id=job.job_id,
        )
        pinned_configuration = self._json_object(
            job.pinned_configuration_json,
            label="pinned configuration",
            job_id=job.job_id,
        )
        try:
            return validate_backup_deep_verify_payload(
                requested_scope=requested_scope,
                pinned_configuration=pinned_configuration,
            )
        except BackupDeepVerifyPayloadError as exc:
            raise BackupDeepVerifyJobError(
                f"Deep verify job {job.job_id} has invalid durable payload."
            ) from exc

    @staticmethod
    def _json_object(
        raw: str | None,
        *,
        label: str,
        job_id: object,
    ) -> dict[str, object]:
        if raw is None:
            raise BackupDeepVerifyJobError(
                f"Deep verify job {job_id} has no {label}."
            )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BackupDeepVerifyJobError(
                f"Deep verify job {job_id} has invalid {label} JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise BackupDeepVerifyJobError(
                f"Deep verify job {job_id} {label} must be an object."
            )
        return payload

    def _wait(
        self,
        job: JobRecord,
        *,
        lease_token: bytes,
        reason: WaitingReason,
    ) -> JobRecord:
        retry_at_us = utc_now_us() + self.retry_seconds * 1_000_000
        return self.jobs.wait(
            job.job_id,
            lease_token=lease_token,
            reason=reason,
            next_run_at_us=retry_at_us,
        )
