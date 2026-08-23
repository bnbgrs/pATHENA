from __future__ import annotations

import uuid

import pytest

from athena.source.models import (
    BlobRecord,
    BlobStorageArea,
    RepresentationRetentionState,
    SourceAnchorRecord,
    SourceAnchorType,
    SourceCaptureResult,
    SourceLifecycleState,
    SourceRecord,
    SourceRepresentationRecord,
    SourceRepresentationType,
    SourceType,
    TextRepresentationResult,
)


_DIGEST = b"d" * 32
_OTHER_DIGEST = b"e" * 32


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _blob(*, blob_id: uuid.UUID | None = None, digest: bytes = _DIGEST) -> BlobRecord:
    return BlobRecord(
        blob_id=blob_id or _uuid(),
        byte_length=10,
        media_type="text/plain",
        storage_area=BlobStorageArea.ARCHIVE,
        storage_locator="sha256/aa/blob",
        integrity_sha256=digest,
        encryption_state="plaintext",
        created_at_us=10,
        verified_at_us=10,
    )


def _source(*, blob: BlobRecord, digest: bytes = _DIGEST) -> SourceRecord:
    return SourceRecord(
        source_id=_uuid(),
        source_type=SourceType.TEXT,
        created_at_us=20,
        acquired_at_us=10,
        original_name=None,
        original_modified_at_us=None,
        mime_type="text/plain",
        blob_id=blob.blob_id,
        content_sha256=digest,
        source_uri=None,
        lifecycle_state=SourceLifecycleState.READY,
        provenance_id=_uuid(),
    )


def _representation(
    *,
    blob: BlobRecord,
    digest: bytes = _DIGEST,
) -> SourceRepresentationRecord:
    return SourceRepresentationRecord(
        representation_id=_uuid(),
        source_id=_uuid(),
        representation_type=SourceRepresentationType.NORMALIZED_TEXT,
        blob_id=blob.blob_id,
        processing_run_id=_uuid(),
        content_hash=digest,
        retention_state=RepresentationRetentionState.RETAINED,
        media_type="text/plain; charset=utf-8",
        parser_id="test.parser",
        parser_version="1",
        options_json="{}",
        created_at_us=20,
        provenance_id=_uuid(),
    )


def test_source_capture_result_requires_matching_blob_identity_and_hash() -> None:
    blob = _blob()
    source = _source(blob=blob)

    result = SourceCaptureResult(source=source, blob=blob, reused_blob=False)

    assert result.blob.blob_id == result.source.blob_id


def test_source_capture_result_rejects_blob_identity_mismatch() -> None:
    blob = _blob()
    source = _source(blob=blob)

    with pytest.raises(ValueError, match="identity mismatch"):
        SourceCaptureResult(source=source, blob=_blob(), reused_blob=False)


def test_source_capture_result_rejects_hash_mismatch() -> None:
    blob = _blob()
    source = _source(blob=blob, digest=_OTHER_DIGEST)

    with pytest.raises(ValueError, match="hash mismatch"):
        SourceCaptureResult(source=source, blob=blob, reused_blob=False)


def test_source_record_rejects_bool_timestamp() -> None:
    blob = _blob()

    with pytest.raises(TypeError, match="created_at_us must be an integer"):
        SourceRecord(
            source_id=_uuid(),
            source_type=SourceType.TEXT,
            created_at_us=True,  # type: ignore[arg-type]
            acquired_at_us=0,
            original_name=None,
            original_modified_at_us=None,
            mime_type=None,
            blob_id=blob.blob_id,
            content_sha256=_DIGEST,
            source_uri=None,
            lifecycle_state=SourceLifecycleState.CAPTURED,
            provenance_id=_uuid(),
        )


def test_representation_rejects_non_sha256_content_hash() -> None:
    blob = _blob()

    with pytest.raises(ValueError, match="32-byte SHA-256"):
        _representation(blob=blob, digest=b"short")


def test_text_representation_result_rejects_hash_mismatch() -> None:
    blob = _blob()
    representation = _representation(blob=blob, digest=_OTHER_DIGEST)

    with pytest.raises(ValueError, match="hash mismatch"):
        TextRepresentationResult(
            representation=representation,
            blob=blob,
            reused_blob=False,
        )


def test_source_anchor_rejects_half_offset_range() -> None:
    with pytest.raises(ValueError, match="both endpoints or neither"):
        SourceAnchorRecord(
            anchor_id=_uuid(),
            source_id=_uuid(),
            representation_id=_uuid(),
            anchor_type=SourceAnchorType.TEXT_RANGE,
            start_offset=0,
            end_offset=None,
            page_start=None,
            page_end=None,
            start_time_ms=None,
            end_time_ms=None,
            geometry_json=None,
            quoted_hash=_DIGEST,
            created_at_us=1,
        )


def test_source_anchor_rejects_bool_range_endpoint() -> None:
    with pytest.raises(TypeError, match="offset range start must be an integer"):
        SourceAnchorRecord(
            anchor_id=_uuid(),
            source_id=_uuid(),
            representation_id=_uuid(),
            anchor_type=SourceAnchorType.TEXT_RANGE,
            start_offset=True,  # type: ignore[arg-type]
            end_offset=2,
            page_start=None,
            page_end=None,
            start_time_ms=None,
            end_time_ms=None,
            geometry_json=None,
            quoted_hash=_DIGEST,
            created_at_us=1,
        )


def test_source_anchor_rejects_reverse_page_range() -> None:
    with pytest.raises(ValueError, match="page range end precedes start"):
        SourceAnchorRecord(
            anchor_id=_uuid(),
            source_id=_uuid(),
            representation_id=_uuid(),
            anchor_type=SourceAnchorType.PAGE_RANGE,
            start_offset=None,
            end_offset=None,
            page_start=3,
            page_end=2,
            start_time_ms=None,
            end_time_ms=None,
            geometry_json=None,
            quoted_hash=None,
            created_at_us=1,
        )
