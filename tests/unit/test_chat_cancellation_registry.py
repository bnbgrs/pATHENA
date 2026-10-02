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

def test_cancel_is_isolated_to_exact_operation() -> None:
    registry = ChatCancellationRegistry()
    first_id = uuid.UUID("11111111-2222-4333-8444-555555555555")
    second_id = uuid.UUID("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee")
    first = registry.reserve(first_id)
    second = registry.reserve(second_id)

    assert first is not None
    assert second is not None
    assert registry.cancel(first_id) is True
    assert first.cancel_requested() is True
    assert second.cancel_requested() is False
    assert registry.is_active(second_id) is True


def test_duplicate_same_id_reservation_is_rejected_without_replacing_owner() -> None:
    registry = ChatCancellationRegistry()
    owner = registry.reserve(_OPERATION_ID)

    assert owner is not None
    assert registry.reserve(_OPERATION_ID) is None
    assert registry.cancel(_OPERATION_ID) is True
    assert owner.cancel_requested() is True

    registry.release(owner)
    assert registry.is_active(_OPERATION_ID) is False
