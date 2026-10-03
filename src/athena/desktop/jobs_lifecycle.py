"""Truthful desktop projection of durable job lifecycle capabilities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

_TERMINAL_STATES = frozenset({"cancelled", "failed", "completed"})
_KNOWN_STATES = frozenset(
    {
        "queued",
        "running",
        "waiting",
        "paused",
        "cancel_requested",
        *_TERMINAL_STATES,
    }
)
_TRANSITION_LABELS = {
    "pause": "JOB_PAUSE",
    "resume": "JOB_RESUME",
    "wake": "JOB_WAKE",
    "cancel": "JOB_CANCEL",
}


class JobLifecycleError(ValueError):
    """Raised when a transition receipt cannot be bound to its request."""


@dataclass(frozen=True)
class JobActionAvailability:
    state: str | None
    pause: bool
    resume: bool
    wake: bool
    cancel: bool

    def reason(self, action: str) -> str:
        enabled = bool(getattr(self, action))
        if enabled:
            return f"{action.title()} is available while this job is {self.state}."
        if self.state is None:
            return "Select a job first."
        if self.state not in _KNOWN_STATES:
            return "This job has an unrecognized state; actions are unavailable."
        if self.state in _TERMINAL_STATES:
            return f"This job is {self.state}; no actions are available."
        if self.state == "cancel_requested":
            return "Cancellation has already been requested and is waiting to complete."
        return f"{action.title()} is unavailable while this job is {self.state}."


@dataclass(frozen=True)
class JobListEntry:
    job_id: str
    state: str
    priority: int
    job_type: str
    stage: str
    retries: int
    updated_at_us: int
    summary: str


@dataclass(frozen=True)
class JobTransitionReceipt:
    operation: str
    job_id: str
    state: str


def parse_job_list(output: str) -> tuple[JobListEntry, ...]:
    """Validate the complete jobs CLI list response before the UI mutates state."""
    entries: list[JobListEntry] = []
    for line_number, raw_line in enumerate(output.splitlines(), start=1):
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) != 8:
            raise JobLifecycleError(
                f"The jobs list response is malformed at line {line_number}."
            )
        (
            raw_job_id,
            raw_state,
            raw_priority,
            job_type,
            stage,
            raw_retries,
            raw_updated_at_us,
            summary,
        ) = parts

        try:
            job_id = str(uuid.UUID(raw_job_id))
        except (ValueError, AttributeError) as exc:
            raise JobLifecycleError(
                f"The jobs list response has an invalid job ID at line {line_number}."
            ) from exc

        state = raw_state.casefold().strip()
        if state not in _KNOWN_STATES:
            raise JobLifecycleError(
                f"The jobs list response has an unrecognized state at line {line_number}."
            )
        if not job_type.strip() or not stage.strip():
            raise JobLifecycleError(
                f"The jobs list response is missing job metadata at line {line_number}."
            )
        try:
            priority = int(raw_priority)
            retries = int(raw_retries)
            updated_at_us = int(raw_updated_at_us)
        except ValueError as exc:
            raise JobLifecycleError(
                f"The jobs list response has invalid numeric data at line {line_number}."
            ) from exc
        if retries < 0 or updated_at_us < 0:
            raise JobLifecycleError(
                f"The jobs list response has invalid numeric data at line {line_number}."
            )

        entries.append(
            JobListEntry(
                job_id=job_id,
                state=state,
                priority=priority,
                job_type=job_type,
                stage=stage,
                retries=retries,
                updated_at_us=updated_at_us,
                summary=summary,
            )
        )
    return tuple(entries)


def action_availability(state: str | None) -> JobActionAvailability:
    """Project only transitions implemented by ``DurableJobService``."""
    normalized = None if state is None else state.casefold().strip()
    known = normalized in _KNOWN_STATES
    return JobActionAvailability(
        state=normalized,
        pause=known and normalized in {"queued", "waiting"},
        resume=known and normalized == "paused",
        wake=known and normalized == "waiting",
        cancel=(
            known
            and normalized not in _TERMINAL_STATES
            and normalized != "cancel_requested"
        ),
    )


def parse_transition_receipt(
    output: str,
    *,
    expected_operation: str,
    expected_job_id: str,
) -> JobTransitionReceipt:
    """Bind a CLI transition receipt to the exact requested job and operation."""
    expected_label = _TRANSITION_LABELS.get(expected_operation)
    if expected_label is None:
        raise JobLifecycleError("This job action is not supported.")
    parts = output.strip().split()
    if len(parts) != 3 or parts[0] != expected_label:
        raise JobLifecycleError("The job action response could not be verified.")
    if parts[1] != expected_job_id:
        raise JobLifecycleError("The job action response belongs to another job.")
    state = parts[2].casefold()
    if state not in _KNOWN_STATES:
        raise JobLifecycleError("The job action response returned an unrecognized state.")
    return JobTransitionReceipt(
        operation=expected_operation,
        job_id=expected_job_id,
        state=state,
    )
