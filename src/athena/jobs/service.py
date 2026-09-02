"""Application-facing durable job use cases."""

from __future__ import annotations

import json
import math
import secrets
import sqlite3
import uuid
from collections.abc import Callable, Mapping
from typing import Any

from athena.chat.service import ChatService
from athena.jobs.models import (
    CheckpointRecord,
    JobPriority,
    JobRecord,
    WaitingReason,
)
from athena.jobs.news_payload_validation import (
    NewsJobPayloadValidationError,
    validate_news_job_payload,
)
from athena.jobs.payload_validation import (
    BuiltinJobPayloadValidationError,
    validate_builtin_job_payload,
)
from athena.jobs.repository import JobRepository
from athena.news.models import NEWS_JOB_TYPE, NEWS_PERIOD_JOB_TYPE


class UnsupportedJobTypeError(ValueError):
    """Raised when a caller tries to persist an unregistered job type."""


class InvalidJobPayloadError(ValueError):
    """Raised when durable job JSON or orchestration scalars are unsafe."""


class DurableJobService:
    """Validated durable job orchestration without an in-memory queue."""

    BUILTIN_JOB_TYPES = frozenset(
        {
            "archive.replicate",
            "backup.create",
            "source.process",
            "source.analyze",
            "source.extract",
            "source.represent",
            "source.chunk",
            "search.rebuild",
            "embedding.rebuild",
            "integrity.sweep",
            "research.exhaustive",
            NEWS_JOB_TYPE,
            NEWS_PERIOD_JOB_TYPE,
        }
    )

    def __init__(self, repository: JobRepository, chat: ChatService) -> None:
        self.repository = repository
        self.chat = chat

    def create(
        self,
        *,
        job_type: str,
        priority: JobPriority = JobPriority.NORMAL,
        requested_scope: Mapping[str, Any] | None = None,
        pinned_configuration: Mapping[str, Any] | None = None,
        next_run_at_us: int | None = None,
    ) -> JobRecord:
        normalized_job_type = self._registered_job_type(job_type)
        normalized_scope = _optional_mapping(requested_scope, "requested_scope")
        normalized_configuration = _optional_mapping(
            pinned_configuration,
            "pinned_configuration",
        )
        _job_priority(priority)
        _optional_nonnegative_int(next_run_at_us, "next_run_at_us")
        try:
            if normalized_job_type in {NEWS_JOB_TYPE, NEWS_PERIOD_JOB_TYPE}:
                validate_news_job_payload(
                    normalized_job_type,
                    requested_scope=normalized_scope,
                    pinned_configuration=normalized_configuration,
                )
            else:
                validate_builtin_job_payload(
                    normalized_job_type,
                    requested_scope=normalized_scope,
                    pinned_configuration=normalized_configuration,
                )
        except (BuiltinJobPayloadValidationError, NewsJobPayloadValidationError) as exc:
            raise InvalidJobPayloadError(str(exc)) from exc

        requested_scope_json = _canonical_json(normalized_scope)
        pinned_configuration_json = _canonical_json(normalized_configuration)
        actor_id = self.chat.ensure_local_user()
        return self.repository.create(
            job_type=normalized_job_type,
            actor_id=actor_id,
            priority=priority,
            requested_scope_json=requested_scope_json,
            pinned_configuration_json=pinned_configuration_json,
            next_run_at_us=next_run_at_us,
        )

    def active_for_type(
        self,
        job_type: str,
        *,
        limit: int = 16,
    ) -> tuple[JobRecord, ...]:
        """Return nonterminal jobs for one registered durable job type."""
        normalized_job_type = self._registered_job_type(job_type)
        _positive_int(limit, "limit")
        return self.repository.list_nonterminal_by_type(
            job_type=normalized_job_type,
            limit=limit,
        )

    def acquire(
        self,
        job_id: uuid.UUID,
        *,
        worker_id: str,
        lease_seconds: int = 60,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _canonical_text(worker_id, "worker_id")
        _positive_int(lease_seconds, "lease_seconds")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.acquire_lease(
            job_id=normalized_job_id,
            worker_id=worker_id,
            lease_token=secrets.token_bytes(32),
            lease_duration_us=lease_seconds * 1_000_000,
            now_us=now_us,
        )

    def heartbeat(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        extend_seconds: int = 60,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)
        _positive_int(extend_seconds, "extend_seconds")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.heartbeat(
            job_id=normalized_job_id,
            lease_token=lease_token,
            extend_by_us=extend_seconds * 1_000_000,
            now_us=now_us,
        )

    def canonical_write_fence(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
    ) -> Callable[[sqlite3.Connection], None]:
        """Return a lease fence for one canonical write transaction."""
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)

        def fence(connection: sqlite3.Connection) -> None:
            self.repository.require_live_write_fence(
                connection,
                job_id=normalized_job_id,
                lease_token=lease_token,
            )

        return fence

    def checkpoint(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        current_stage: str | None,
        progress_state: Mapping[str, Any] | None = None,
        last_confirmed_input: Mapping[str, Any] | None = None,
        last_confirmed_output: Mapping[str, Any] | None = None,
        resume_metadata: Mapping[str, Any] | None = None,
        processing_stage_id: uuid.UUID | None = None,
        commit_id: uuid.UUID | None = None,
        now_us: int | None = None,
    ) -> CheckpointRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        normalized_processing_stage_id = _optional_uuid_value(
            processing_stage_id,
            "processing_stage_id",
        )
        normalized_commit_id = _optional_uuid_value(commit_id, "commit_id")
        normalized_progress = _optional_mapping(progress_state, "progress_state")
        normalized_input = _optional_mapping(
            last_confirmed_input,
            "last_confirmed_input",
        )
        normalized_output = _optional_mapping(
            last_confirmed_output,
            "last_confirmed_output",
        )
        normalized_resume = _optional_mapping(resume_metadata, "resume_metadata")
        _lease_token(lease_token)
        _optional_canonical_text(current_stage, "current_stage")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.add_checkpoint(
            job_id=normalized_job_id,
            lease_token=lease_token,
            processing_stage_id=normalized_processing_stage_id,
            progress_state_json=_canonical_json(normalized_progress),
            last_confirmed_input_json=_canonical_json(normalized_input),
            last_confirmed_output_json=_canonical_json(normalized_output),
            resume_metadata_json=_canonical_json(normalized_resume),
            commit_id=normalized_commit_id,
            current_stage=current_stage,
            now_us=now_us,
        )

    def recover_startup(self, *, now_us: int | None = None) -> tuple[JobRecord, ...]:
        """Recover only expired leases; live worker leases are never stolen."""
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.recover_expired_leases(now_us=now_us)

    def get(self, job_id: uuid.UUID) -> JobRecord:
        return self.repository.get(_uuid_value(job_id, "job_id"))

    def list(self, *, limit: int = 100) -> tuple[JobRecord, ...]:
        _positive_int(limit, "limit")
        return self.repository.list(limit=limit)

    def eligible_queued(
        self,
        *,
        now_us: int,
        job_types: set[str] | frozenset[str] | None = None,
        limit: int = 128,
    ) -> tuple[JobRecord, ...]:
        _nonnegative_int(now_us, "now_us")
        _positive_int(limit, "limit")
        normalized_job_types = self._registered_job_type_filter(job_types)
        return self.repository.list_eligible_queued(
            now_us=now_us,
            job_types=normalized_job_types,
            limit=limit,
        )

    def waiting(self, *, limit: int = 128) -> tuple[JobRecord, ...]:
        _positive_int(limit, "limit")
        return self.repository.list_waiting(limit=limit)

    def wake_due_waiting(
        self,
        *,
        now_us: int | None = None,
    ) -> tuple[JobRecord, ...]:
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.wake_due_waiting(now_us=now_us)

    def schedule_retry(
        self,
        job_id: uuid.UUID,
        *,
        next_run_at_us: int,
        max_retries: int,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _nonnegative_int(next_run_at_us, "next_run_at_us")
        _nonnegative_int(max_retries, "max_retries")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.schedule_retry(
            normalized_job_id,
            next_run_at_us=next_run_at_us,
            max_retries=max_retries,
            now_us=now_us,
        )

    def yield_job(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        next_run_at_us: int | None = None,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)
        _optional_nonnegative_int(next_run_at_us, "next_run_at_us")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.yield_job(
            job_id=normalized_job_id,
            lease_token=lease_token,
            next_run_at_us=next_run_at_us,
            now_us=now_us,
        )

    def checkpoints(self, job_id: uuid.UUID) -> tuple[CheckpointRecord, ...]:
        return self.repository.list_checkpoints(_uuid_value(job_id, "job_id"))

    def get_checkpoint(self, checkpoint_id: uuid.UUID) -> CheckpointRecord:
        return self.repository.get_checkpoint(_uuid_value(checkpoint_id, "checkpoint_id"))

    def fail(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        blocked_reason: str,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)
        _canonical_text(blocked_reason, "blocked_reason")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.fail(
            job_id=normalized_job_id,
            lease_token=lease_token,
            blocked_reason=blocked_reason,
            now_us=now_us,
        )

    def wait(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        reason: WaitingReason,
        next_run_at_us: int | None = None,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)
        _waiting_reason(reason)
        _optional_nonnegative_int(next_run_at_us, "next_run_at_us")
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.wait(
            job_id=normalized_job_id,
            lease_token=lease_token,
            reason=reason,
            next_run_at_us=next_run_at_us,
            now_us=now_us,
        )

    def wake(self, job_id: uuid.UUID) -> JobRecord:
        return self.repository.wake(_uuid_value(job_id, "job_id"))

    def request_cancel(self, job_id: uuid.UUID) -> JobRecord:
        return self.repository.request_cancel(_uuid_value(job_id, "job_id"))

    def pause(self, job_id: uuid.UUID) -> JobRecord:
        return self.repository.pause(_uuid_value(job_id, "job_id"))

    def resume(self, job_id: uuid.UUID) -> JobRecord:
        return self.repository.resume(_uuid_value(job_id, "job_id"))

    def complete(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.complete(
            job_id=normalized_job_id,
            lease_token=lease_token,
            now_us=now_us,
        )

    def acknowledge_cancel(
        self,
        job_id: uuid.UUID,
        *,
        lease_token: bytes,
        now_us: int | None = None,
    ) -> JobRecord:
        normalized_job_id = _uuid_value(job_id, "job_id")
        _lease_token(lease_token)
        _optional_nonnegative_int(now_us, "now_us")
        return self.repository.acknowledge_cancel(
            job_id=normalized_job_id,
            lease_token=lease_token,
            now_us=now_us,
        )

    def _registered_job_type(self, value: object) -> str:
        job_type = _canonical_text(value, "job_type")
        if job_type not in self.BUILTIN_JOB_TYPES:
            raise UnsupportedJobTypeError(
                f"Unregistered ATHENA job type {job_type!r}."
            )
        return job_type

    def _registered_job_type_filter(
        self,
        value: object,
    ) -> set[str] | frozenset[str] | None:
        if value is None:
            return None
        if not isinstance(value, (set, frozenset)):
            raise InvalidJobPayloadError(
                "job_types must be a set or frozenset of registered job type strings."
            )
        normalized: set[str] = set()
        for item in value:
            normalized.add(self._registered_job_type(item))
        return normalized


def _optional_mapping(
    value: object | None,
    label: str,
) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise InvalidJobPayloadError(f"{label} must be a JSON object mapping.")
    return value


def _canonical_json(value: Mapping[str, Any] | None) -> str | None:
    if value is None:
        return None
    _require_json_value(value, path="$", top_level=True)
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidJobPayloadError("Job payload must be finite canonical JSON.") from exc


def _require_json_value(
    value: object,
    *,
    path: str,
    top_level: bool = False,
) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        if top_level:
            raise InvalidJobPayloadError("Durable JSON payload must be an object mapping.")
        return
    if isinstance(value, float):
        if top_level:
            raise InvalidJobPayloadError("Durable JSON payload must be an object mapping.")
        if not math.isfinite(value):
            raise InvalidJobPayloadError(f"Job payload value at {path} must be finite.")
        return
    if isinstance(value, list):
        if top_level:
            raise InvalidJobPayloadError("Durable JSON payload must be an object mapping.")
        for index, item in enumerate(value):
            _require_json_value(item, path=f"{path}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise InvalidJobPayloadError(
                    f"Job payload object key at {path} must be text."
                )
            _require_json_value(item, path=f"{path}.{key}")
        return
    raise InvalidJobPayloadError(
        f"Job payload value at {path} has unsupported type {type(value).__name__!r}."
    )


def _uuid_value(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise InvalidJobPayloadError(f"{label} must be a UUID value.")
    return value


def _optional_uuid_value(value: object | None, label: str) -> uuid.UUID | None:
    if value is None:
        return None
    return _uuid_value(value, label)


def _job_priority(value: object) -> JobPriority:
    if not isinstance(value, JobPriority):
        raise InvalidJobPayloadError("priority must be a JobPriority value.")
    return value


def _waiting_reason(value: object) -> WaitingReason:
    if not isinstance(value, WaitingReason):
        raise InvalidJobPayloadError("reason must be a WaitingReason value.")
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvalidJobPayloadError(f"{label} must be an integer >= 1.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidJobPayloadError(f"{label} must be an integer >= 0.")
    return value


def _optional_nonnegative_int(value: object | None, label: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, label)


def _canonical_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise InvalidJobPayloadError(f"{label} must be non-empty canonical text.")
    return value


def _optional_canonical_text(value: object | None, label: str) -> str | None:
    if value is None:
        return None
    return _canonical_text(value, label)


def _lease_token(value: object) -> bytes:
    if not isinstance(value, bytes) or len(value) != 32:
        raise InvalidJobPayloadError("lease_token must contain exactly 32 bytes.")
    return value
