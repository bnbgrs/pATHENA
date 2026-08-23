"""Domain models for immutable Raw Archive source capture."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum


class SourceType(str, Enum):
    """Logical source types defined by the v1 persistent data model."""

    FILE = "file"
    WEB_SNAPSHOT = "web_snapshot"
    EMAIL = "email"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    API_CAPTURE = "api_capture"
    CHAT_EXPORT = "chat_export"
    OTHER = "other"


class SourceLifecycleState(str, Enum):
    """Technical processing state of a captured Source."""

    CAPTURED = "captured"
    PROCESSING = "processing"
    READY = "ready"
    PARTIAL = "partial"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    CANCELLED = "cancelled"


class BlobStorageArea(str, Enum):
    """Physical area containing the verified immutable blob bytes."""

    ARCHIVE = "archive"
    SPOOL = "spool"


class SourceRepresentationType(str, Enum):
    """Technical representations derived from immutable Source bytes."""

    NORMALIZED_TEXT = "normalized_text"
    EXTRACTED_TEXT = "extracted_text"


class SourceRepresentationStructureType(str, Enum):
    """Retained technical structure extracted from a document representation."""

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"


class SourceAnchorType(str, Enum):
    """Stable source location types from the persistent data model."""

    WHOLE_SOURCE = "whole_source"
    TEXT_RANGE = "text_range"
    PAGE_RANGE = "page_range"
    PAGE_REGION = "page_region"
    AUDIO_TIME_RANGE = "audio_time_range"
    VIDEO_TIME_RANGE = "video_time_range"
    TABLE_CELL = "table_cell"
    MESSAGE = "message"
    STRUCTURED_PATH = "structured_path"


class RepresentationRetentionState(str, Enum):
    """Whether one immutable representation is retained for durable provenance."""

    RETAINED = "retained"
    DISPOSABLE = "disposable"


def _require_uuid(value: object, label: str) -> None:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")


def _require_int(value: object, label: str, *, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}.")


def _require_sha256(value: object, label: str) -> None:
    if not isinstance(value, bytes):
        raise TypeError(f"{label} must be bytes.")
    if len(value) != 32:
        raise ValueError(f"{label} must be a 32-byte SHA-256 digest.")


def _require_text(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value.strip():
        raise ValueError(f"{label} must not be empty.")


def _require_optional_uuid(value: object | None, label: str) -> None:
    if value is not None:
        _require_uuid(value, label)


def _require_optional_text(value: object | None, label: str) -> None:
    if value is not None and not isinstance(value, str):
        raise TypeError(f"{label} must be text or None.")


def _require_optional_int(value: object | None, label: str, *, minimum: int = 0) -> None:
    if value is not None:
        _require_int(value, label, minimum=minimum)


@dataclass(frozen=True, slots=True)
class BlobRecord:
    blob_id: uuid.UUID
    byte_length: int
    media_type: str | None
    storage_area: BlobStorageArea
    storage_locator: str
    integrity_sha256: bytes
    encryption_state: str
    created_at_us: int
    verified_at_us: int

    def __post_init__(self) -> None:
        _require_uuid(self.blob_id, "BlobRecord blob_id")
        _require_int(self.byte_length, "BlobRecord byte_length")
        _require_optional_text(self.media_type, "BlobRecord media_type")
        if not isinstance(self.storage_area, BlobStorageArea):
            raise TypeError("BlobRecord storage_area must be a BlobStorageArea.")
        _require_text(self.storage_locator, "BlobRecord storage_locator")
        _require_sha256(self.integrity_sha256, "BlobRecord integrity_sha256")
        _require_text(self.encryption_state, "BlobRecord encryption_state")
        _require_int(self.created_at_us, "BlobRecord created_at_us")
        _require_int(self.verified_at_us, "BlobRecord verified_at_us")
        if self.verified_at_us < self.created_at_us:
            raise ValueError("BlobRecord verified_at_us precedes created_at_us.")


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_id: uuid.UUID
    source_type: SourceType
    created_at_us: int
    acquired_at_us: int
    original_name: str | None
    original_modified_at_us: int | None
    mime_type: str | None
    blob_id: uuid.UUID
    content_sha256: bytes
    source_uri: str | None
    lifecycle_state: SourceLifecycleState
    provenance_id: uuid.UUID
    protection_scope_id: uuid.UUID | None = None
    protected_metadata_payload_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        _require_uuid(self.source_id, "SourceRecord source_id")
        _require_uuid(self.blob_id, "SourceRecord blob_id")
        _require_uuid(self.provenance_id, "SourceRecord provenance_id")
        _require_optional_uuid(self.protection_scope_id, "SourceRecord protection_scope_id")
        _require_optional_uuid(
            self.protected_metadata_payload_id,
            "SourceRecord protected_metadata_payload_id",
        )
        if not isinstance(self.source_type, SourceType):
            raise TypeError("SourceRecord source_type must be a SourceType.")
        if not isinstance(self.lifecycle_state, SourceLifecycleState):
            raise TypeError(
                "SourceRecord lifecycle_state must be a SourceLifecycleState."
            )
        _require_int(self.created_at_us, "SourceRecord created_at_us")
        _require_int(self.acquired_at_us, "SourceRecord acquired_at_us")
        _require_optional_int(
            self.original_modified_at_us,
            "SourceRecord original_modified_at_us",
        )
        _require_optional_text(self.original_name, "SourceRecord original_name")
        _require_optional_text(self.mime_type, "SourceRecord mime_type")
        _require_optional_text(self.source_uri, "SourceRecord source_uri")
        _require_sha256(self.content_sha256, "SourceRecord content_sha256")


@dataclass(frozen=True, slots=True)
class SourceCaptureResult:
    source: SourceRecord
    blob: BlobRecord
    reused_blob: bool

    def __post_init__(self) -> None:
        if not isinstance(self.source, SourceRecord):
            raise TypeError("SourceCaptureResult source must be a SourceRecord.")
        if not isinstance(self.blob, BlobRecord):
            raise TypeError("SourceCaptureResult blob must be a BlobRecord.")
        if not isinstance(self.reused_blob, bool):
            raise TypeError("SourceCaptureResult reused_blob must be boolean.")
        if self.source.blob_id != self.blob.blob_id:
            raise ValueError("SourceCaptureResult source/blob identity mismatch.")
        if self.source.content_sha256 != self.blob.integrity_sha256:
            raise ValueError("SourceCaptureResult source/blob hash mismatch.")


@dataclass(frozen=True, slots=True)
class SourceRepresentationRecord:
    representation_id: uuid.UUID
    source_id: uuid.UUID
    representation_type: SourceRepresentationType
    blob_id: uuid.UUID
    processing_run_id: uuid.UUID
    content_hash: bytes
    retention_state: RepresentationRetentionState
    media_type: str
    parser_id: str
    parser_version: str
    options_json: str
    created_at_us: int
    provenance_id: uuid.UUID

    def __post_init__(self) -> None:
        for value, label in (
            (self.representation_id, "Source representation representation_id"),
            (self.source_id, "Source representation source_id"),
            (self.blob_id, "Source representation blob_id"),
            (self.processing_run_id, "Source representation processing_run_id"),
            (self.provenance_id, "Source representation provenance_id"),
        ):
            _require_uuid(value, label)
        if not isinstance(self.representation_type, SourceRepresentationType):
            raise TypeError(
                "Source representation representation_type must be a SourceRepresentationType."
            )
        if not isinstance(self.retention_state, RepresentationRetentionState):
            raise TypeError(
                "Source representation retention_state must be a RepresentationRetentionState."
            )
        _require_sha256(self.content_hash, "Source representation content_hash")
        _require_text(self.media_type, "Source representation media_type")
        _require_text(self.parser_id, "Source representation parser_id")
        _require_text(self.parser_version, "Source representation parser_version")
        _require_text(self.options_json, "Source representation options_json")
        _require_int(self.created_at_us, "Source representation created_at_us")


@dataclass(frozen=True, slots=True)
class SourceRepresentationPageRecord:
    representation_id: uuid.UUID
    page_number: int
    start_offset: int
    end_offset: int
    content_hash: bytes

    def __post_init__(self) -> None:
        _require_uuid(self.representation_id, "Source representation page representation_id")
        _require_int(self.page_number, "Source representation page page_number", minimum=1)
        _require_int(self.start_offset, "Source representation page start_offset")
        _require_int(self.end_offset, "Source representation page end_offset")
        if self.end_offset < self.start_offset:
            raise ValueError("Source representation page end_offset precedes start_offset.")
        _require_sha256(self.content_hash, "Source representation page content_hash")


@dataclass(frozen=True, slots=True)
class SourceRepresentationStructureRecord:
    structure_id: uuid.UUID
    representation_id: uuid.UUID
    structure_index: int
    structure_type: SourceRepresentationStructureType
    path: str
    parent_structure_id: uuid.UUID | None
    start_offset: int
    end_offset: int
    content_hash: bytes
    metadata_json: str

    def __post_init__(self) -> None:
        _require_uuid(self.structure_id, "Source representation structure_id")
        _require_uuid(
            self.representation_id,
            "Source representation structure representation_id",
        )
        _require_optional_uuid(
            self.parent_structure_id,
            "Source representation structure parent_structure_id",
        )
        _require_int(self.structure_index, "Source representation structure_index")
        if not isinstance(self.structure_type, SourceRepresentationStructureType):
            raise TypeError(
                "Source representation structure_type must be a "
                "SourceRepresentationStructureType."
            )
        _require_text(self.path, "Source representation structure path")
        _require_int(self.start_offset, "Source representation structure start_offset")
        _require_int(self.end_offset, "Source representation structure end_offset")
        if self.end_offset < self.start_offset:
            raise ValueError("Source representation structure end_offset precedes start_offset.")
        _require_sha256(self.content_hash, "Source representation structure content_hash")
        _require_text(self.metadata_json, "Source representation structure metadata_json")


@dataclass(frozen=True, slots=True)
class TextRepresentationResult:
    representation: SourceRepresentationRecord
    blob: BlobRecord
    reused_blob: bool

    def __post_init__(self) -> None:
        if not isinstance(self.representation, SourceRepresentationRecord):
            raise TypeError(
                "TextRepresentationResult representation must be a SourceRepresentationRecord."
            )
        if not isinstance(self.blob, BlobRecord):
            raise TypeError("TextRepresentationResult blob must be a BlobRecord.")
        if not isinstance(self.reused_blob, bool):
            raise TypeError("TextRepresentationResult reused_blob must be boolean.")
        if self.representation.blob_id != self.blob.blob_id:
            raise ValueError("TextRepresentationResult representation/blob identity mismatch.")
        if self.representation.content_hash != self.blob.integrity_sha256:
            raise ValueError("TextRepresentationResult representation/blob hash mismatch.")


@dataclass(frozen=True, slots=True)
class SourceAnchorRecord:
    anchor_id: uuid.UUID
    source_id: uuid.UUID
    representation_id: uuid.UUID | None
    anchor_type: SourceAnchorType
    start_offset: int | None
    end_offset: int | None
    page_start: int | None
    page_end: int | None
    start_time_ms: int | None
    end_time_ms: int | None
    geometry_json: str | None
    quoted_hash: bytes | None
    created_at_us: int

    def __post_init__(self) -> None:
        _require_uuid(self.anchor_id, "SourceAnchorRecord anchor_id")
        _require_uuid(self.source_id, "SourceAnchorRecord source_id")
        _require_optional_uuid(
            self.representation_id,
            "SourceAnchorRecord representation_id",
        )
        if not isinstance(self.anchor_type, SourceAnchorType):
            raise TypeError("SourceAnchorRecord anchor_type must be a SourceAnchorType.")
        self._validate_pair(
            self.start_offset,
            self.end_offset,
            label="SourceAnchorRecord offset range",
            minimum=0,
        )
        self._validate_pair(
            self.page_start,
            self.page_end,
            label="SourceAnchorRecord page range",
            minimum=1,
        )
        self._validate_pair(
            self.start_time_ms,
            self.end_time_ms,
            label="SourceAnchorRecord time range",
            minimum=0,
        )
        _require_optional_text(self.geometry_json, "SourceAnchorRecord geometry_json")
        if self.quoted_hash is not None:
            _require_sha256(self.quoted_hash, "SourceAnchorRecord quoted_hash")
        _require_int(self.created_at_us, "SourceAnchorRecord created_at_us")

    @staticmethod
    def _validate_pair(
        start: int | None,
        end: int | None,
        *,
        label: str,
        minimum: int,
    ) -> None:
        if (start is None) != (end is None):
            raise ValueError(f"{label} must provide both endpoints or neither.")
        if start is None or end is None:
            return
        _require_int(start, f"{label} start", minimum=minimum)
        _require_int(end, f"{label} end", minimum=minimum)
        if end < start:
            raise ValueError(f"{label} end precedes start.")
