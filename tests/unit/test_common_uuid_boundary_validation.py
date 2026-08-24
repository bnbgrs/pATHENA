from __future__ import annotations

import uuid
from typing import Any

import pytest

from athena.common.ids import uuid_from_blob, uuid_to_blob

VALUE = uuid.UUID("12345678-1234-4234-8234-123456789abc")


@pytest.mark.parametrize(
    "value",
    [None, True, False, 0, 1, "12345678-1234-4234-8234-123456789abc", b"x" * 16],
)
def test_uuid_to_blob_rejects_non_uuid(value: Any) -> None:
    with pytest.raises(TypeError):
        uuid_to_blob(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [None, True, False, 0, 1, "x" * 16, bytearray(16), memoryview(b"x" * 16)],
)
def test_uuid_from_blob_rejects_non_bytes(value: Any) -> None:
    with pytest.raises(TypeError):
        uuid_from_blob(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [b"", b"x" * 15, b"x" * 17, b"x" * 32])
def test_uuid_from_blob_rejects_wrong_byte_length(value: bytes) -> None:
    with pytest.raises(ValueError, match="16 bytes"):
        uuid_from_blob(value)


def test_uuid_binary_roundtrip_is_exact() -> None:
    payload = uuid_to_blob(VALUE)

    assert isinstance(payload, bytes)
    assert len(payload) == 16
    assert uuid_from_blob(payload) == VALUE
