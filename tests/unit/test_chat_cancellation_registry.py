from __future__ import annotations

import uuid

from athena.chat.cancellation import ChatCancellationRegistry


_OPERATION_ID = uuid.UUID("11111111-2222-4333-8444-555555555555")


def test_unknown_cancel_never_creates_a_tombstone() -> None:
    registry = ChatCancellationRegistry()

    assert registry.cancel(_OPERATION_ID) is False
    assert registry.is_active(_OPERATION_ID) is False


def test_reserved_operation_can_be_cancelled_idempotently_until_release() -> None:
    registry = ChatCancellationRegistry()
    reservation = registry.reserve(_OPERATION_ID)

    assert reservation is not None
    assert reservation.cancel_requested() is False
    assert registry.cancel(_OPERATION_ID) is True
    assert reservation.cancel_requested() is True
    assert registry.cancel(_OPERATION_ID) is True

    registry.release(reservation)

    assert registry.is_active(_OPERATION_ID) is False
    assert registry.cancel(_OPERATION_ID) is False


def test_stale_release_cannot_remove_a_newer_reservation() -> None:
    registry = ChatCancellationRegistry()
    first = registry.reserve(_OPERATION_ID)
    assert first is not None

    registry.release(first)
    second = registry.reserve(_OPERATION_ID)
    assert second is not None
    assert second is not first

    registry.release(first)

    assert registry.is_active(_OPERATION_ID) is True
    assert registry.cancel(_OPERATION_ID) is True
    assert second.cancel_requested() is True
