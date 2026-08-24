from __future__ import annotations

import json
import uuid

import pytest

from athena.security.service import ProtectedContentIntegrityError
from athena.source.models import SourceType
from athena.source.protected_blob import (
    PROTECTED_BLOB_CHUNK_SIZE,
    ProtectedSourceMetadata,
    _chunk_aad,
)


def _payload(**overrides: object) -> bytes:
    data: dict[str, object] = {
        "format_version": 1,
        "mime_type": "text/plain",
        "original_modified_at_us": 123,
        "original_name": "note.txt",
        "plaintext_byte_length": 5,
        "source_type": SourceType.FILE.value,
        "source_uri": "file:///tmp/note.txt",
    }
    data.update(overrides)
    return json.dumps(
        data,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


@pytest.mark.parametrize(
    "payload",
    [
        "not-bytes",
        bytearray(b"{}"),
        b"[]",
        _payload(format_version=True),
        _payload(format_version=1.0),
        _payload(original_modified_at_us=True),
        _payload(original_modified_at_us=-1),
        _payload(plaintext_byte_length=True),
        _payload(plaintext_byte_length=-1),
        _payload(source_type="unknown"),
        _payload(original_name=""),
        _payload(source_uri=""),
    ],
)
def test_protected_source_metadata_rejects_malformed_persisted_payload(
    payload: object,
) -> None:
    with pytest.raises(ProtectedContentIntegrityError):
        ProtectedSourceMetadata.from_payload(payload)  # type: ignore[arg-type]


def test_protected_source_metadata_rejects_extra_persisted_field() -> None:
    data = json.loads(_payload().decode("ascii"))
    data["extra"] = "unexpected"
    encoded = json.dumps(
        data,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")

    with pytest.raises(ProtectedContentIntegrityError):
        ProtectedSourceMetadata.from_payload(encoded)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_type", "file"),
        ("original_name", 123),
        ("source_uri", 123),
        ("original_modified_at_us", True),
        ("original_modified_at_us", -1),
        ("mime_type", 123),
        ("plaintext_byte_length", True),
        ("plaintext_byte_length", -1),
    ],
)
def test_protected_source_metadata_direct_construction_is_fail_closed(
    field: str,
    value: object,
) -> None:
    kwargs: dict[str, object] = {
        "source_type": SourceType.FILE,
        "original_name": "note.txt",
        "source_uri": "file:///tmp/note.txt",
        "original_modified_at_us": 123,
        "mime_type": "text/plain",
        "plaintext_byte_length": 5,
    }
    kwargs[field] = value

    with pytest.raises(ProtectedContentIntegrityError):
        ProtectedSourceMetadata(**kwargs)  # type: ignore[arg-type]


def test_protected_source_metadata_current_roundtrip() -> None:
    current = ProtectedSourceMetadata(
        source_type=SourceType.FILE,
        original_name="note.txt",
        source_uri="file:///tmp/note.txt",
        original_modified_at_us=123,
        mime_type="text/plain",
        plaintext_byte_length=5,
    )

    assert ProtectedSourceMetadata.from_payload(current.to_payload()) == current


@pytest.mark.parametrize(
    ("chunk_index", "plaintext_length"),
    [
        (True, 1),
        (-1, 1),
        (0x1_0000_0000, 1),
        (0, True),
        (0, 0),
        (0, PROTECTED_BLOB_CHUNK_SIZE + 1),
    ],
)
def test_protected_blob_aad_rejects_invalid_scalar_boundaries(
    chunk_index: object,
    plaintext_length: object,
) -> None:
    with pytest.raises(ValueError):
        _chunk_aad(
            blob_id=uuid.uuid4(),
            protection_scope_id=uuid.uuid4(),
            chunk_index=chunk_index,  # type: ignore[arg-type]
            plaintext_length=plaintext_length,  # type: ignore[arg-type]
        )


def test_protected_blob_aad_accepts_current_boundary_values() -> None:
    blob_id = uuid.uuid4()
    scope_id = uuid.uuid4()

    first = _chunk_aad(
        blob_id=blob_id,
        protection_scope_id=scope_id,
        chunk_index=0,
        plaintext_length=1,
    )
    last = _chunk_aad(
        blob_id=blob_id,
        protection_scope_id=scope_id,
        chunk_index=0xFFFFFFFF,
        plaintext_length=PROTECTED_BLOB_CHUNK_SIZE,
    )

    assert first.startswith(b"ATHENA\x00PROTECTED_BLOB_CHUNK\x00")
    assert last.startswith(b"ATHENA\x00PROTECTED_BLOB_CHUNK\x00")
