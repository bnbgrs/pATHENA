"""Transport-neutral v1 Search Response contracts.

These DTOs live on the existing ``athena.api`` client boundary. They serialize
only provenance/classification facts already established by retrieval code and
do not perform search, authorization, persistence, or ranking themselves.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.api.contracts import ApiContract


def _nonempty_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value.strip():
        raise ValueError(f"{label} must not be empty.")
    return value


def _uuid_text(value: object, label: str) -> str:
    text = _nonempty_text(value, label)
    try:
        parsed = uuid.UUID(text)
    except ValueError as exc:
        raise ValueError(f"{label} must be a UUID.") from exc
    if str(parsed) != text.lower():
        raise ValueError(f"{label} must use canonical UUID text.")
    return text


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 1:
        raise ValueError(f"{label} must be positive.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")
    return value


@dataclass(frozen=True, slots=True)
class SearchSourceAnchorResponse(ApiContract):
    """Stable, non-persisting SourceAnchor materialization inputs."""

    representation_id: str
    start_offset: int
    end_offset: int
    quoted_sha256: str

    def __post_init__(self) -> None:
        _uuid_text(self.representation_id, "Search source representation_id")
        start = _nonnegative_int(self.start_offset, "Search source start_offset")
        end = _nonnegative_int(self.end_offset, "Search source end_offset")
        if end <= start:
            raise ValueError(
                "Search source range must satisfy start_offset < end_offset."
            )
        digest = _nonempty_text(self.quoted_sha256, "Search source quoted_sha256")
        if len(digest) != 64:
            raise ValueError("Search source quoted_sha256 must be a SHA-256 hex digest.")
        try:
            bytes.fromhex(digest)
        except ValueError as exc:
            raise ValueError(
                "Search source quoted_sha256 must be a SHA-256 hex digest."
            ) from exc


@dataclass(frozen=True, slots=True)
class SearchProtectionResponse(ApiContract):
    """Protection classification, not transient unlock state."""

    state: str
    protection_scope_id: str | None

    def __post_init__(self) -> None:
        state = _nonempty_text(self.state, "Search protection state")
        if state == "unprotected":
            if self.protection_scope_id is not None:
                raise ValueError(
                    "Unprotected Search responses must not expose a protection scope."
                )
            return
        if state != "protected":
            raise ValueError("Search protection state is unknown.")
        if self.protection_scope_id is None:
            raise ValueError(
                "Protected Search responses must retain their protection scope."
            )
        _uuid_text(
            self.protection_scope_id,
            "Search protection protection_scope_id",
        )


@dataclass(frozen=True, slots=True)
class SearchResultResponse(ApiContract):
    """Canonical transport-neutral result shape required by Beta Search §52."""

    result_ref: str
    title: str | None
    preview: str
    entity_type: str
    revision_id: str
    rank: int
    retrieval_methods: tuple[str, ...]
    source_anchor: SearchSourceAnchorResponse | None
    protection: SearchProtectionResponse

    def __post_init__(self) -> None:
        _nonempty_text(self.result_ref, "Search result_ref")
        if self.title is not None and not isinstance(self.title, str):
            raise TypeError("Search title must be text or None.")
        if not isinstance(self.preview, str):
            raise TypeError("Search preview must be text.")
        _nonempty_text(self.entity_type, "Search entity_type")
        _uuid_text(self.revision_id, "Search revision_id")
        _positive_int(self.rank, "Search rank")
        if not isinstance(self.retrieval_methods, tuple):
            raise TypeError("Search retrieval_methods must be a tuple.")
        if not self.retrieval_methods:
            raise ValueError("Search retrieval_methods must not be empty.")
        for method in self.retrieval_methods:
            _nonempty_text(method, "Search retrieval method")
        if len(set(self.retrieval_methods)) != len(self.retrieval_methods):
            raise ValueError("Search retrieval_methods must be unique.")
        if self.source_anchor is not None and not isinstance(
            self.source_anchor,
            SearchSourceAnchorResponse,
        ):
            raise TypeError(
                "Search source_anchor must be a SearchSourceAnchorResponse or None."
            )
        if not isinstance(self.protection, SearchProtectionResponse):
            raise TypeError("Search protection must be a SearchProtectionResponse.")
