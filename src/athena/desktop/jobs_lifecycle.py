"""Truthful desktop projection of durable job lifecycle capabilities."""

from __future__ import annotations

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
            return f"{action.title()} is supported for persisted state {self.state}."
        if self.state is None:
            return "Select a durable job first."
        if self.state in _TERMINAL_STATES:
            return f"Job is terminal ({self.state}); no lifecycle mutation is available."
        if self.state == "cancel_requested":
            return (
                "Cancellation is already persisted (cancel_requested) and awaits "
                "worker acknowledgement."
            )
        return f"{action.title()} is not supported for persisted state {self.state}."


@dataclass(frozen=True)
class JobTransitionReceipt:
    operation: str
    job_id: str
    state: str


def action_availability(state: str | None) -> JobActionAvailability:
    """Project only transitions implemented by ``DurableJobService``."""
    normalized = None if state is None else state.casefold().strip()
    return JobActionAvailability(
        state=normalized,
        pause=normalized in {"queued", "waiting"},
        resume=normalized == "paused",
        wake=normalized == "waiting",
        cancel=(
            normalized is not None
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
        raise JobLifecycleError("Unsupported lifecycle operation.")
    parts = output.strip().split()
    if len(parts) != 3 or parts[0] != expected_label:
        raise JobLifecycleError("Durable job transition receipt is invalid.")
    if parts[1] != expected_job_id:
        raise JobLifecycleError("Durable job transition receipt belongs to another job.")
    state = parts[2].casefold()
    if state not in _KNOWN_STATES:
        raise JobLifecycleError("Durable job transition returned an unknown state.")
    return JobTransitionReceipt(
        operation=expected_operation,
        job_id=expected_job_id,
        state=state,
    )
