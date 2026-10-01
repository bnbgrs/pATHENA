"""Thread-safe out-of-band cancellation state for active chat sends."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field


class ChatOperationActiveError(RuntimeError):
    """Raised when the same send operation is already active."""


@dataclass(frozen=True, slots=True)
class ChatCancellationReservation:
    """Identity-stable cancellation token for exactly one active send."""

    operation_id: uuid.UUID
    _event: threading.Event = field(repr=False, compare=False)

    def cancel_requested(self) -> bool:
        """Return whether cancellation has been requested for this reservation."""
        return self._event.is_set()


class ChatCancellationRegistry:
    """Bounded registry containing only reserved or active chat operations.

    Unknown cancellation requests never create entries. Release removes an
    entry only when the exact reservation object still owns the operation slot,
    so stale cleanup cannot remove a newer reservation that reused the same
    operation identifier.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active: dict[uuid.UUID, ChatCancellationReservation] = {}

    def reserve(
        self,
        operation_id: uuid.UUID,
    ) -> ChatCancellationReservation | None:
        """Reserve an operation before it is queued onto the Core owner thread."""
        with self._lock:
            if operation_id in self._active:
                return None
            reservation = ChatCancellationReservation(
                operation_id=operation_id,
                _event=threading.Event(),
            )
            self._active[operation_id] = reservation
            return reservation

    def get_or_reserve(
        self,
        operation_id: uuid.UUID,
    ) -> ChatCancellationReservation:
        """Return a pre-reservation or create one for direct in-thread callers."""
        with self._lock:
            current = self._active.get(operation_id)
            if current is not None:
                return current
            reservation = ChatCancellationReservation(
                operation_id=operation_id,
                _event=threading.Event(),
            )
            self._active[operation_id] = reservation
            return reservation

    def cancel(self, operation_id: uuid.UUID) -> bool:
        """Signal one known active operation without creating tombstones."""
        with self._lock:
            reservation = self._active.get(operation_id)
            if reservation is None:
                return False
            reservation._event.set()
            return True

    def release(self, reservation: ChatCancellationReservation) -> None:
        """Release only the exact reservation that still owns its operation slot."""
        with self._lock:
            current = self._active.get(reservation.operation_id)
            if current is reservation:
                del self._active[reservation.operation_id]

    def is_active(self, operation_id: uuid.UUID) -> bool:
        """Return whether the operation currently owns a registry slot."""
        with self._lock:
            return operation_id in self._active
