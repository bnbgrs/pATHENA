from __future__ import annotations

import uuid

import pytest

from athena.source.models import (
    BlobRecord,
    BlobStorageArea,
    SourceRepresentationPageRecord,
    SourceRepresentationStructureRecord,
    SourceRepresentationStructureType,
)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _blob(**overrides: object) -> BlobRecord:
    values: dict[str, object] = {
        "blob_id": _uuid(),
        "byte_length": 10,
        "media_type": "text/plain",
        "storage_area": BlobStorageArea.SPOOL,
        "storage_locator": "ab/cd/blob.bin",
        "integrity_sha256": b"x" * 32,
        "encryption_state": "none",
        "created_at_us": 10,
        "verified_at_us": 11,
    }
    values.update(overrides)
    return BlobRecord(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("byte_length", [True, 1.5, "10", -1])
def test_blob_rejects_invalid_byte_length(byte_length: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _blob(byte_length=byte_length)


def test_blob_rejects_invalid_digest_length() -> None:
    with pytest.raises(ValueError, match="32-byte SHA-256"):
        _blob(integrity_sha256=b"short")


def test_blob_rejects_reverse_verification_timestamp() -> None:
    with pytest.raises(ValueError, match="precedes created_at_us"):
        _blob(created_at_us=20, verified_at_us=19)


@pytest.mark.parametrize("page_number", [True, 0, -1, 1.5])
def test_page_record_rejects_invalid_page_number(page_number: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        SourceRepresentationPageRecord(
            representation_id=_uuid(),
            page_number=page_number,  # type: ignore[arg-type]
            start_offset=0,
            end_offset=1,
            content_hash=b"x" * 32,
        )


def test_page_record_rejects_reverse_range() -> None:
    with pytest.raises(ValueError, match="precedes start_offset"):
        SourceRepresentationPageRecord(
            representation_id=_uuid(),
            page_number=1,
            start_offset=2,
            end_offset=1,
            content_hash=b"x" * 32,
        )


def test_structure_record_rejects_bool_offset() -> None:
    with pytest.raises(TypeError, match="start_offset must be an integer"):
        SourceRepresentationStructureRecord(
            structure_id=_uuid(),
            representation_id=_uuid(),
            structure_index=0,
            structure_type=SourceRepresentationStructureType.PARAGRAPH,
            path="/body/p[1]",
            parent_structure_id=None,
            start_offset=True,  # type: ignore[arg-type]
            end_offset=1,
            content_hash=b"x" * 32,
            metadata_json="{}",
        )


def test_structure_record_rejects_reverse_range() -> None:
    with pytest.raises(ValueError, match="precedes start_offset"):
        SourceRepresentationStructureRecord(
            structure_id=_uuid(),
            representation_id=_uuid(),
            structure_index=0,
            structure_type=SourceRepresentationStructureType.PARAGRAPH,
            path="/body/p[1]",
            parent_structure_id=None,
            start_offset=3,
            end_offset=2,
            content_hash=b"x" * 32,
            metadata_json="{}",
        )
