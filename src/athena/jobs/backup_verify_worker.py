"""Durable execution primitive for periodic Deep backup verification.

This worker deliberately sits on top of the existing deterministic planner and
``BackupService.verify_deep``. It does not duplicate backup verification,
restore-smoke, target locking, or persistence semantics. Runtime registration
and scheduler composition are provided by the surrounding durable-job stack.
"""

from __future__ import annotations

import json
import uuid

from athena.backup.service import BackupRestoreError, BackupService
from athena.backup.target_lock import BackupTargetBusyError
from athena.common.time import utc_now_us
from athena.jobs.backup_verify import select_deep_verify_candidate
from athena.jobs.models import JobPriority, JobRecord, JobState, WaitingReason
from athena.jobs.service import DurableJobService

BACKUP_DEEP_VERIFY_JOB_TYPE = "backup.verify_deep"

_PIPELINE_VERSION = "backup-deep-verify-v1"
_DEFAULT_INTERVAL_SECONDS = 7 * 24 * 60 * 60
_DEFAULT_RETRY_SECONDS = 5 * 60
_DEFAULT_LEASE_EXTENSION_SECONDS = 30 * 60
_JOB_SCAN_LIMIT = 4096


class BackupDeepVerifyJobError(RuntimeError):
    """Raised when a durable Deep-verification job cannot continue safely."""


def _positive_seconds(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be an integer >= 1.")
    return value


def _nonnegative_timestamp(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


class DurableBackupDeepVerifyWorker:
    """Plan and execute retry-safe periodic Deep verification work.

    ``BackupService.verify_deep`` remains the sole owner of target locking,
    full object hashing, isolated restore smoke, and verification-state writes.
    This class owns only durable-job orchestration around that primitive.
    """

    def __init__(
        self,
        *,
        jobs: DurableJobService,
        backup: BackupService,
        interval_seconds: int = _DEFAULT_INTERVAL_SECONDS,
        retry_seconds: int = _DEFAULT_RETRY_SECONDS,
        lease_extension_seconds: int = _DEFAULT_LEASE_EXTENSION_SECONDS,
    ) -> None:
        self.jobs = jobs
        self.backup = backup
        self.interval_seconds = _positive_seconds(
            interval_seconds,
            label="Deep verification interval_seconds",
        )
        self.retry_seconds = _positive_seconds(
            retry_seconds,
            label="Deep verification retry_seconds",
        )
        self.lease_extension_seconds = _positive_seconds(
            lease_extension_seconds,
            label="Deep verification lease_extension_seconds",
        )

    def schedule_due(
        self,
        *,
        now_us: int | None = None,
    ) -> tuple[JobRecord, ...]:
        """Persist at most one deterministic due verification occurrence.

        The planner intentionally selects one oldest-due restore point.  This
        keeps periodic verification bounded and avoids a restart-triggered job
        storm.  Subsequent scheduler ticks can enqueue the next due snapshot.
        """
        now = (
            utc_now_us()
            if now_us is None
            else _nonnegative_timestamp(now_us, label="now_us")
        )
        candidate = select_deep_verify_candidate(
            self.backup,
            now_us=now,
            interval_seconds=self.interval_seconds,
        )
        if candidate is None:
            return ()

        if self._has_active_target_job(candidate.target_id):
            return ()

        if self._has_job_for_occurrence(
            candidate.snapshot_id,
            candidate.occurrence_slot_us,
        ):
            return ()

        return (
            self.jobs.create(
                job_type=BACKUP_DEEP_VERIFY_JOB_TYPE,
                priority=JobPriority.MAINTENANCE,
                requested_scope={
                    "occurrence_slot_us": candidate.occurrence_slot_us,
                    "snapshot_id": str(candidate.snapshot_id),
                    "target_id": str(candidate.target_id),
                },
                pinned_configuration={
                    "interval_seconds": self.interval_seconds,
                    "pipeline_version": _PIPELINE_VERSION,
                },
            ),
        )

    def process_leased(self, job: JobRecord) -> JobRecord:
        """Execute one leased Deep-verification occurrence safely."""
        if job.job_type != BACKUP_DEEP_VERIFY_JOB_TYPE:
            raise BackupDeepVerifyJobError(
                f"Unexpected backup verification job type {job.job_type!r}."
            )

        lease_token = job.lease_token
        if lease_token is None:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has no live lease token."
            )

        if job.state is JobState.CANCEL_REQUESTED:
            return self.jobs.acknowledge_cancel(
                job.job_id,
                lease_token=lease_token,
            )

        if job.state is not JobState.RUNNING:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} is not running."
            )

        snapshot_id, target_id, occurrence_slot_us = self._job_scope(job)

        try:
            record = self.backup.get_snapshot(snapshot_id)
        except BackupRestoreError as exc:
            raise BackupDeepVerifyJobError(
                f"Backup snapshot {snapshot_id} is unavailable for verification."
            ) from exc

        if record.target_id != target_id:
            raise BackupDeepVerifyJobError(
                "Backup verification job target does not match snapshot provenance."
            )

        # Retention or another maintenance action may have made a queued
        # occurrence obsolete.  It must not resurrect a pruned restore point.
        if record.state != "complete" or record.pruned_at_us is not None:
            return self.jobs.complete(
                job.job_id,
                lease_token=lease_token,
            )

        # A manual Deep verification may have satisfied this occurrence while
        # the durable job was still queued.  Treat that as idempotent success.
        if (
            record.verification_status == "verified_deep"
            and record.last_verified_at_us is not None
            and record.last_verified_at_us >= occurrence_slot_us
        ):
            return self.jobs.complete(
                job.job_id,
                lease_token=lease_token,
            )

        try:
            target = self.backup.target_status(target_id)
        except BackupTargetBusyError:
            return self._wait(
                job,
                lease_token=lease_token,
                reason=WaitingReason.BACKOFF,
            )
        except BackupRestoreError as exc:
            raise BackupDeepVerifyJobError(
                f"Backup target {target_id} failed identity validation."
            ) from exc

        if target.status == "retired":
            return self.jobs.complete(
                job.job_id,
                lease_token=lease_token,
            )

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
            return self._wait_after_environment_failure(
                job,
                lease_token=lease_token,
                target_id=target_id,
            )
        except BackupRestoreError as exc:
            # ``verify_deep`` records a real integrity failure when the target
            # remains active.  Environment/offline failures deliberately keep
            # the restore point retryable and are translated into WAITING.
            try:
                refreshed_target = self.backup.target_status(target_id)
            except BackupTargetBusyError:
                return self._wait(
                    job,
                    lease_token=lease_token,
                    reason=WaitingReason.BACKOFF,
                )
            except BackupRestoreError:
                refreshed_target = None

            if refreshed_target is not None and refreshed_target.status != "active":
                return self._wait(
                    job,
                    lease_token=lease_token,
                    reason=WaitingReason.STORAGE,
                )

            raise BackupDeepVerifyJobError(
                f"Deep verification failed for snapshot {snapshot_id}."
            ) from exc

        if verified.snapshot_id != snapshot_id or verified.target_id != target_id:
            raise BackupDeepVerifyJobError(
                "Deep verification returned a different snapshot identity."
            )
        if (
            verified.verification_status != "verified_deep"
            or verified.last_verified_at_us is None
        ):
            raise BackupDeepVerifyJobError(
                "Deep verification completed without durable verified_deep state."
            )

        self.jobs.checkpoint(
            job.job_id,
            lease_token=lease_token,
            current_stage="backup_deep_verify_complete",
            progress_state={
                "occurrence_slot_us": occurrence_slot_us,
                "snapshot_id": str(snapshot_id),
                "target_id": str(target_id),
                "verification_status": verified.verification_status,
            },
            last_confirmed_output={
                "last_verified_at_us": verified.last_verified_at_us,
                "snapshot_id": str(snapshot_id),
            },
        )

        return self.jobs.complete(
            job.job_id,
            lease_token=lease_token,
        )

    def _has_active_target_job(self, target_id: uuid.UUID) -> bool:
        for job in self.jobs.active_for_type(
            BACKUP_DEEP_VERIFY_JOB_TYPE,
            limit=_JOB_SCAN_LIMIT,
        ):
            _, candidate_target, _ = self._job_scope(job)
            if candidate_target == target_id:
                return True
        return False

    def _has_job_for_occurrence(
        self,
        snapshot_id: uuid.UUID,
        occurrence_slot_us: int,
    ) -> bool:
        for job in self.jobs.list(limit=_JOB_SCAN_LIMIT):
            if job.job_type != BACKUP_DEEP_VERIFY_JOB_TYPE:
                continue
            candidate_snapshot, _, candidate_slot = self._job_scope(job)
            if (
                candidate_snapshot == snapshot_id
                and candidate_slot == occurrence_slot_us
            ):
                return True
        return False

    def _job_scope(
        self,
        job: JobRecord,
    ) -> tuple[uuid.UUID, uuid.UUID, int]:
        raw = job.requested_scope_json
        if raw is None:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has no requested scope."
            )

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has invalid scope JSON."
            ) from exc

        if not isinstance(payload, dict) or set(payload) != {
            "occurrence_slot_us",
            "snapshot_id",
            "target_id",
        }:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has invalid scope fields."
            )

        snapshot_raw = payload.get("snapshot_id")
        target_raw = payload.get("target_id")
        slot_raw = payload.get("occurrence_slot_us")
        if not isinstance(snapshot_raw, str) or not isinstance(target_raw, str):
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has invalid identities."
            )
        if isinstance(slot_raw, bool) or not isinstance(slot_raw, int) or slot_raw < 0:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has invalid occurrence slot."
            )

        try:
            snapshot_id = uuid.UUID(snapshot_raw)
            target_id = uuid.UUID(target_raw)
        except ValueError as exc:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} has invalid UUID scope."
            ) from exc

        if str(snapshot_id) != snapshot_raw or str(target_id) != target_raw:
            raise BackupDeepVerifyJobError(
                f"Backup verification job {job.job_id} UUID scope is not canonical."
            )

        return snapshot_id, target_id, slot_raw

    def _wait_after_environment_failure(
        self,
        job: JobRecord,
        *,
        lease_token: bytes,
        target_id: uuid.UUID,
    ) -> JobRecord:
        try:
            target = self.backup.target_status(target_id)
        except BackupTargetBusyError:
            reason = WaitingReason.BACKOFF
        except BackupRestoreError:
            reason = WaitingReason.BACKOFF
        else:
            reason = (
                WaitingReason.STORAGE
                if target.status != "active"
                else WaitingReason.BACKOFF
            )
        return self._wait(
            job,
            lease_token=lease_token,
            reason=reason,
        )

    def _wait(
        self,
        job: JobRecord,
        *,
        lease_token: bytes,
        reason: WaitingReason,
    ) -> JobRecord:
        now_us = utc_now_us()
        return self.jobs.wait(
            job.job_id,
            lease_token=lease_token,
            reason=reason,
            next_run_at_us=now_us + self.retry_seconds * 1_000_000,
            now_us=now_us,
        )
