"""Deterministic Search Response source-anchor references for archive retrieval."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol


class _ArchiveAnchorInputs(Protocol):
    representation_id: uuid.UUID
    start_anchor_value: int
    end_anchor_value: int
    content_hash: bytes


@dataclass(frozen=True, slots=True)
class SearchSourceAnchorRef:
    """Stable, non-persisting inputs for a durable text SourceAnchor.

    This value does not create a SourceAnchor row. It preserves the exact
    representation/range/hash tuple already verified by archive retrieval so
    callers can expose deterministic Search Response provenance without
    inventing an anchor id or mutating canonical state during search.
    """

    representation_id: uuid.UUID
    start_offset: int
    end_offset: int
    quoted_hash: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.representation_id, uuid.UUID):
            raise TypeError("Search source anchor representation_id must be a UUID.")
        if isinstance(self.start_offset, bool) or not isinstance(self.start_offset, int):
            raise TypeError("Search source anchor start_offset must be an integer.")
        if isinstance(self.end_offset, bool) or not isinstance(self.end_offset, int):
            raise TypeError("Search source anchor end_offset must be an integer.")
        if self.start_offset < 0:
            raise ValueError("Search source anchor start_offset must not be negative.")
        if self.end_offset <= self.start_offset:
            raise ValueError("Search source anchor range must satisfy start_offset < end_offset.")
        if not isinstance(self.quoted_hash, bytes):
            raise TypeError("Search source anchor quoted_hash must be bytes.")
        if len(self.quoted_hash) != 32:
            raise ValueError("Search source anchor quoted_hash must be a SHA-256 digest.")

    @property
    def stable_key(self) -> tuple[uuid.UUID, int, int, bytes]:
        return (
            self.representation_id,
            self.start_offset,
            self.end_offset,
            self.quoted_hash,
        )


def source_anchor_ref(result: _ArchiveAnchorInputs) -> SearchSourceAnchorRef:
    """Project verified archive result fields into a stable source-anchor ref."""

    return SearchSourceAnchorRef(
        representation_id=result.representation_id,
        start_offset=result.start_anchor_value,
        end_offset=result.end_anchor_value,
        quoted_hash=result.content_hash,
    )
