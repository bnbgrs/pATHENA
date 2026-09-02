import uuid

import pytest

from athena.common import ids
from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob


def test_uuid7_has_standard_version_and_variant() -> None:
    value = new_uuid7()

    assert value.version == 7
    assert value.variant == uuid.RFC_4122
    assert len(value.bytes) == 16


def test_uuid7_preserves_unix_millisecond_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    timestamp_ms = 1_787_508_000_123
    monkeypatch.setattr(ids.time, "time_ns", lambda: timestamp_ms * 1_000_000)

    value = new_uuid7()

    assert value.int >> 80 == timestamp_ms


@pytest.mark.parametrize(
    "time_ns",
    [
        -1_000_000,
        (((1 << 48) - 1) + 1) * 1_000_000,
    ],
)
def test_uuid7_rejects_clock_values_outside_rfc_timestamp_range(
    monkeypatch: pytest.MonkeyPatch,
    time_ns: int,
) -> None:
    monkeypatch.setattr(ids.time, "time_ns", lambda: time_ns)

    with pytest.raises(RuntimeError, match="outside the RFC 9562 UUIDv7 timestamp range"):
        new_uuid7()


def test_uuid_blob_roundtrip() -> None:
    value = new_uuid7()

    assert uuid_from_blob(uuid_to_blob(value)) == value
