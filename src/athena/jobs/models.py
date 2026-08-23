"""Persistent job and checkpoint value objects."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from enum import Enum, IntEnum


class JobPriority(IntEnum):
    """Stable ATHENA priority classes; lower values run first."""

    DATA_SAFETY = 0
    INTERACTIVE = 1
    TIME_CRITICAL = 2
    NORMAL = 3
    BACKGROUND = 4
    MAINTENANCE = 5


class JobState(str, Enum):
    """Normative durable job states."""

    QUEUED = "queued"
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"

    @property
    def terminal(self) -> bool:
        return self in {self.CANCELLED, self.FAILED, self.COMPLETED}


class WaitingReason(str, Enum):
    """Machine-readable reasons for the generic waiting state."""

    RESOURCE = "waiting_resource"
    STORAGE = "waiting_storage"
    NETWORK = "waiting_network"
    DEPENDENCY = "waiting_dependency"
    SCHEDULE = "waiting_schedule"
    USER = "waiting_user"
    BACKOFF = "waiting_backoff"


def _require_uuid(value: object, label: str) -> None:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")


def _require_optional_uuid(value: object | None, label: str) -> None:
    if value is not None:
        _require_uuid(value, label)


def _require_int(value: object, label: str, *, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}.")


def _require_optional_int(value: object | None, label: str, *, minimum: int = 0) -> None:
    if value is not None:
        _require_int(value, label, minimum=minimum)


def _require_text(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value:
        raise ValueError(f"{label} must not be empty.")
    if value != value.strip():
        raise ValueError(f"{label} must use canonical trimmed text.")


def _require_optional_text(value: object | None, label: str) -> None:
    if value is None:
        return
    _require_text(value, label)


def _require_optional_json(value: object | None, label: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise TypeError(f"{label} must be JSON text or None.")
    try:
        json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must contain valid JSON.") from exc


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: uuid.UUID
    job_type: str
    created_at_us: int
    created_by_actor_id: uuid.UUID
    priority: JobPriority
    state: JobState
    requested_scope_json: str | None
    processing_run_id: uuid.UUID | None
    current_stage: str | None
    last_checkpoint_id: uuid.UUID | None
    retry_count: int
    next_run_at_us: int | None
    blocked_reason: str | None
    pinned_configuration_json: str | None
    protection_scope_id: uuid.UUID | None
    protected_payload_id: uuid.UUID | None
    worker_id: str | None
    lease_token: bytes | None
    lease_acquired_at_us: int | None
    lease_expires_at_us: int | None
    heartbeat_at_us: int | None
    fencing_sequence: int
    updated_at_us: int

    def __post_init__(self) -> None:
        _require_uuid(self.job_id, "JobRecord job_id")
        _require_uuid(self.created_by_actor_id, "JobRecord created_by_actor_id")
        for uuid_value, label in (
            (self.processing_run_id, "JobRecord processing_run_id"),
            (self.last_checkpoint_id, "JobRecord last_checkpoint_id"),
            (self.protection_scope_id, "JobRecord protection_scope_id"),
            (self.protected_payload_id, "JobRecord protected_payload_id"),
        ):
            _require_optional_uuid(uuid_value, label)
        _require_text(self.job_type, "JobRecord job_type")
        if not isinstance(self.priority, JobPriority):
            raise TypeError("JobRecord priority must be a JobPriority.")
        if not isinstance(self.state, JobState):
            raise TypeError("JobRecord state must be a JobState.")
        _require_optional_json(self.requested_scope_json, "JobRecord requested_scope_json")
        _require_optional_json(
            self.pinned_configuration_json,
            "JobRecord pinned_configuration_json",
        )
        for text_value, label in (
            (self.current_stage, "JobRecord current_stage"),
            (self.blocked_reason, "JobRecord blocked_reason"),
            (self.worker_id, "JobRecord worker_id"),
        ):
            _require_optional_text(text_value, label)
        _require_int(self.created_at_us, "JobRecord created_at_us")
        _require_int(self.updated_at_us, "JobRecord updated_at_us")
        if self.updated_at_us < self.created_at_us:
            raise ValueError("JobRecord updated_at_us precedes created_at_us.")
        _require_int(self.retry_count, "JobRecord retry_count")
        _require_int(self.fencing_sequence, "JobRecord fencing_sequence")
        for int_value, label in (
            (self.next_run_at_us, "JobRecord next_run_at_us"),
            (self.lease_acquired_at_us, "JobRecord lease_acquired_at_us"),
            (self.lease_expires_at_us, "JobRecord lease_expires_at_us"),
            (self.heartbeat_at_us, "JobRecord heartbeat_at_us"),
        ):
            _require_optional_int(int_value, label)
        if self.lease_token is not None:
            if not isinstance(self.lease_token, bytes):
                raise TypeError("JobRecord lease_token must be bytes or None.")
            if not self.lease_token:
                raise ValueError("JobRecord lease_token must not be empty.")
        if (
            self.lease_acquired_at_us is not None
            and self.lease_expires_at_us is not None
            and self.lease_expires_at_us < self.lease_acquired_at_us
        ):
            raise ValueError("JobRecord lease_expires_at_us precedes lease_acquired_at_us.")

    @property
    def uri(self) -> str:
        return f"operational://job/{self.job_id}"


@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    checkpoint_id: uuid.UUID
    job_id: uuid.UUID
    processing_stage_id: uuid.UUID | None
    created_at_us: int
    progress_state_json: str | None
    last_confirmed_input_json: str | None
    last_confirmed_output_json: str | None
    resume_metadata_json: str | None
    commit_id: uuid.UUID | None
    protection_scope_id: uuid.UUID | None
    protected_payload_id: uuid.UUID | None
    fencing_sequence: int

    def __post_init__(self) -> None:
        _require_uuid(self.checkpoint_id, "CheckpointRecord checkpoint_id")
        _require_uuid(self.job_id, "CheckpointRecord job_id")
        for uuid_value, label in (
            (self.processing_stage_id, "CheckpointRecord processing_stage_id"),
            (self.commit_id, "CheckpointRecord commit_id"),
            (self.protection_scope_id, "CheckpointRecord protection_scope_id"),
            (self.protected_payload_id, "CheckpointRecord protected_payload_id"),
        ):
            _require_optional_uuid(uuid_value, label)
        _require_int(self.created_at_us, "CheckpointRecord created_at_us")
        _require_int(self.fencing_sequence, "CheckpointRecord fencing_sequence")
        for json_value, label in (
            (self.progress_state_json, "CheckpointRecord progress_state_json"),
            (self.last_confirmed_input_json, "CheckpointRecord last_confirmed_input_json"),
            (self.last_confirmed_output_json, "CheckpointRecord last_confirmed_output_json"),
            (self.resume_metadata_json, "CheckpointRecord resume_metadata_json"),
        ):
            _require_optional_json(json_value, label)

    @property
    def uri(self) -> str:
        return f"operational://checkpoint/{self.checkpoint_id}"
