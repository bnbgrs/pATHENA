"""Core-owned ephemeral execution context for one model generation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum


class ModelSessionState(str, Enum):
    """Lifecycle state for one temporary Primary Model execution."""

    CREATED = "created"
    STREAMING = "streaming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


_TERMINAL_STATES = frozenset(
    {
        ModelSessionState.COMPLETED,
        ModelSessionState.CANCELLED,
        ModelSessionState.FAILED,
    }
)


class ModelSessionStateError(RuntimeError):
    """Raised when a generation session transition violates its lifecycle."""


def _require_uuid(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")
    return value


def _require_positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 1:
        raise ValueError(f"{label} must be positive.")
    return value


def _require_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")
    return value


@dataclass(slots=True)
class ModelSession:
    """Ephemeral Core-owned identity and state for one provider generation.

    The session contains execution control only. It is not conversation memory
    and does not make provider/backend state canonical. Durable provenance stays
    in ModelSignature/ProcessingRun records. ``context_budget`` is the optional
    retrieval/context allocation and may be zero for direct chat.
    """

    request_id: uuid.UUID
    model_signature_id: uuid.UUID
    context_budget: int
    output_reserve: int
    processing_run_id: uuid.UUID | None = None
    state: ModelSessionState = ModelSessionState.CREATED
    cancel_requested: bool = False
    emitted_delta_count: int = 0

    def __post_init__(self) -> None:
        _require_uuid(self.request_id, "ModelSession request_id")
        _require_uuid(
            self.model_signature_id,
            "ModelSession model_signature_id",
        )
        _require_nonnegative_int(
            self.context_budget,
            "ModelSession context_budget",
        )
        _require_positive_int(
            self.output_reserve,
            "ModelSession output_reserve",
        )
        if self.processing_run_id is not None:
            _require_uuid(
                self.processing_run_id,
                "ModelSession processing_run_id",
            )
        if not isinstance(self.state, ModelSessionState):
            raise TypeError("ModelSession state must be a ModelSessionState.")
        if not isinstance(self.cancel_requested, bool):
            raise TypeError("ModelSession cancel_requested must be bool.")
        _require_nonnegative_int(
            self.emitted_delta_count,
            "ModelSession emitted_delta_count",
        )
        if self.state is ModelSessionState.CREATED:
            if self.emitted_delta_count:
                raise ValueError(
                    "A created ModelSession must not report emitted deltas."
                )
            if self.cancel_requested:
                raise ValueError(
                    "A created ModelSession must not carry a pending cancel request."
                )
        if self.state is ModelSessionState.CANCELLED and not self.cancel_requested:
            raise ValueError(
                "A cancelled ModelSession must retain its cancel request."
            )
        if (
            self.state in {
                ModelSessionState.COMPLETED,
                ModelSessionState.FAILED,
            }
            and self.cancel_requested
        ):
            raise ValueError(
                "Completed or failed ModelSession must not retain a cancel request."
            )

    @property
    def request_key(self) -> str:
        """Return the canonical provider-facing request identifier."""
        return str(self.request_id)

    @property
    def terminal(self) -> bool:
        return self.state in _TERMINAL_STATES

    def begin_streaming(self) -> None:
        if self.state is not ModelSessionState.CREATED:
            raise ModelSessionStateError(
                "ModelSession may begin streaming only from created state."
            )
        if self.cancel_requested:
            self.state = ModelSessionState.CANCELLED
            raise ModelSessionStateError(
                "Cancelled ModelSession must not start provider streaming."
            )
        self.state = ModelSessionState.STREAMING

    def record_delta(self) -> None:
        if self.state is not ModelSessionState.STREAMING:
            raise ModelSessionStateError(
                "ModelSession may record deltas only while streaming."
            )
        if self.cancel_requested:
            raise ModelSessionStateError(
                "ModelSession must discard provider deltas after cancellation."
            )
        self.emitted_delta_count += 1

    def request_cancel(self) -> bool:
        """Request cancellation and report whether provider work may be active."""
        if self.state in _TERMINAL_STATES:
            return False
        self.cancel_requested = True
        if self.state is ModelSessionState.CREATED:
            self.state = ModelSessionState.CANCELLED
            return False
        return True

    def complete(self) -> None:
        if self.state is not ModelSessionState.STREAMING:
            raise ModelSessionStateError(
                "ModelSession may complete only from streaming state."
            )
        if self.cancel_requested:
            self.state = ModelSessionState.CANCELLED
            raise ModelSessionStateError(
                "Cancelled ModelSession must discard late provider completion."
            )
        self.state = ModelSessionState.COMPLETED

    def cancel(self) -> None:
        if self.state in {
            ModelSessionState.COMPLETED,
            ModelSessionState.FAILED,
        }:
            raise ModelSessionStateError(
                "Completed or failed ModelSession cannot become cancelled."
            )
        self.cancel_requested = True
        self.state = ModelSessionState.CANCELLED

    def fail(self) -> None:
        if self.state is not ModelSessionState.STREAMING:
            raise ModelSessionStateError(
                "ModelSession may fail only from streaming state."
            )
        if self.cancel_requested:
            self.state = ModelSessionState.CANCELLED
            return
        self.state = ModelSessionState.FAILED
