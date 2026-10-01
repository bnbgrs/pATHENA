"""Canonical deterministic commit bundles for structured replication.

The serializer intentionally accepts already-selected replication records. It does not
read storage or decide which domain fields are safe to replicate. Callers remain
responsible for supplying only neutral public metadata for protected records; sensitive
metadata belongs in encrypted payloads or opaque protected-payload references.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

FORMAT = "athena.canonical-commit-bundle"
FORMAT_VERSION = 1

# RFC 8785 operates on the I-JSON number domain. This implementation deliberately
# accepts only integers from the exact IEEE-754 safe range and rejects floats, keeping
# the supported canonical number domain small and unambiguous.
MAX_SAFE_INTEGER = (1 << 53) - 1

_ALLOWED_PAYLOAD_KINDS = frozenset({"json", "ciphertext", "protected_ref"})
_BODY_KEYS = frozenset(
    {
        "commit_id",
        "commit_seq",
        "format",
        "format_version",
        "previous_hash",
        "records",
        "schema_version",
    }
)
_RECORD_KEYS = frozenset(
    {
        "metadata",
        "payload",
        "payload_kind",
        "protected",
        "record_id",
        "record_type",
        "schema_version",
    }
)


class CanonicalCommitBundleError(ValueError):
    """Raised when a replication bundle violates the canonical contract."""


@dataclass(frozen=True, slots=True)
class CanonicalCommitRecord:
    """One already-selected structured replication record.

    metadata must contain only neutral, non-sensitive metadata when protected is
    true. The serializer can enforce payload representation shape, but semantic
    metadata sanitization must be proven by the upstream record builder/selector.
    """

    record_type: str
    record_id: str
    schema_version: int
    metadata: Mapping[str, Any]
    payload_kind: str
    payload: Any
    protected: bool = False


@dataclass(frozen=True, slots=True)
class CanonicalCommitBundle:
    data: bytes
    bundle_hash: str


def _validate_unicode_text(value: str, path: str) -> None:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CanonicalCommitBundleError(
            f"Invalid Unicode scalar value at {path}."
        ) from exc


def _require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CanonicalCommitBundleError(f"{name} must be non-empty text.")
    _validate_unicode_text(value, name)
    return value


def _uuid_text(value: uuid.UUID, name: str) -> str:
    if not isinstance(value, uuid.UUID):
        raise CanonicalCommitBundleError(f"{name} must be a UUID.")
    return str(value)


def _positive_integer(value: int, name: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
        or value > MAX_SAFE_INTEGER
    ):
        raise CanonicalCommitBundleError(
            f"{name} must be a positive RFC 8785 safe integer."
        )
    return value


def _hash(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise CanonicalCommitBundleError(
            "previous_hash must contain 64 hex characters."
        )
    normalized = value.lower()
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        raise CanonicalCommitBundleError(
            "previous_hash must contain 64 hex characters."
        ) from exc
    return normalized


def _validate_json(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        _validate_unicode_text(value, path)
        return
    if isinstance(value, int):
        if value < -MAX_SAFE_INTEGER or value > MAX_SAFE_INTEGER:
            raise CanonicalCommitBundleError(
                f"Integer outside the RFC 8785 safe range at {path}."
            )
        return
    if isinstance(value, float):
        raise CanonicalCommitBundleError(
            f"Floating-point values are forbidden at {path}."
        )
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalCommitBundleError(
                    f"Object keys must be strings at {path}."
                )
            _validate_unicode_text(key, f"{path}.<key>")
            _validate_json(item, f"{path}.{key}")
        return
    raise CanonicalCommitBundleError(
        f"Unsupported canonical JSON value at {path}."
    )


def _utf16_sort_key(value: str) -> bytes:
    """Return RFC 8785 / ECMAScript property-order bytes for a valid string."""

    _validate_unicode_text(value, "$.<key>")
    return value.encode("utf-16-be")


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _canonicalize(value[key])
            for key in sorted(value, key=_utf16_sort_key)
        }
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    return value


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    materialized = dict(value)
    _validate_json(materialized)
    canonical = _canonicalize(materialized)
    return json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _record_sort_key(record: CanonicalCommitRecord) -> tuple[bytes, bytes, int]:
    return (
        _utf16_sort_key(record.record_type),
        _utf16_sort_key(record.record_id),
        record.schema_version,
    )


def _record_object(record: CanonicalCommitRecord) -> dict[str, Any]:
    record_type = _require_text(record.record_type, "record_type")
    record_id = _require_text(record.record_id, "record_id")
    schema_version = _positive_integer(record.schema_version, "schema_version")
    if record.payload_kind not in _ALLOWED_PAYLOAD_KINDS:
        raise CanonicalCommitBundleError("Unsupported payload_kind.")
    if not isinstance(record.protected, bool):
        raise CanonicalCommitBundleError("protected must be boolean.")
    if record.protected and record.payload_kind == "json":
        raise CanonicalCommitBundleError(
            "Protected records may not materialize plaintext JSON payloads."
        )
    try:
        metadata = dict(record.metadata)
    except (TypeError, ValueError) as exc:
        raise CanonicalCommitBundleError(
            "metadata must be a JSON object mapping."
        ) from exc
    _validate_json(metadata, "$.metadata")
    _validate_json(record.payload, "$.payload")
    return {
        "metadata": metadata,
        "payload": record.payload,
        "payload_kind": record.payload_kind,
        "protected": record.protected,
        "record_id": record_id,
        "record_type": record_type,
        "schema_version": schema_version,
    }


def serialize_canonical_commit_bundle(
    *,
    commit_id: uuid.UUID,
    commit_seq: int,
    schema_version: int,
    previous_hash: str | None,
    records: Sequence[CanonicalCommitRecord],
) -> CanonicalCommitBundle:
    """Serialize already-selected replication records into canonical bundle bytes."""

    identifier = _uuid_text(commit_id, "commit_id")
    sequence = _positive_integer(commit_seq, "commit_seq")
    schema = _positive_integer(schema_version, "schema_version")

    keyed: list[
        tuple[tuple[bytes, bytes, int], tuple[str, str, int], dict[str, Any]]
    ] = []
    seen: set[tuple[str, str, int]] = set()
    for record in records:
        obj = _record_object(record)
        identity = (
            record.record_type,
            record.record_id,
            record.schema_version,
        )
        if identity in seen:
            raise CanonicalCommitBundleError(
                "Duplicate canonical record identity."
            )
        seen.add(identity)
        keyed.append((_record_sort_key(record), identity, obj))
    keyed.sort(key=lambda item: item[0])

    body: dict[str, Any] = {
        "commit_id": identifier,
        "commit_seq": sequence,
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "previous_hash": _hash(previous_hash),
        "records": [obj for _, _, obj in keyed],
        "schema_version": schema,
    }
    body_bytes = _canonical_bytes(body)
    envelope = {
        "body": body,
        "integrity": {
            "algorithm": "sha256",
            "body_sha256": hashlib.sha256(body_bytes).hexdigest(),
        },
    }
    data = _canonical_bytes(envelope)
    return CanonicalCommitBundle(
        data=data,
        bundle_hash=hashlib.sha256(data).hexdigest(),
    )


def _record_from_object(value: Any, index: int) -> CanonicalCommitRecord:
    if not isinstance(value, dict) or set(value) != _RECORD_KEYS:
        raise CanonicalCommitBundleError(
            f"Invalid canonical record at index {index}."
        )
    metadata = value["metadata"]
    if not isinstance(metadata, dict):
        raise CanonicalCommitBundleError(
            f"Canonical record metadata must be an object at index {index}."
        )
    return CanonicalCommitRecord(
        record_type=value["record_type"],
        record_id=value["record_id"],
        schema_version=value["schema_version"],
        metadata=metadata,
        payload_kind=value["payload_kind"],
        payload=value["payload"],
        protected=value["protected"],
    )


def verify_canonical_commit_bundle(data: bytes) -> CanonicalCommitBundle:
    """Verify integrity, semantics and the exact canonical byte representation."""

    if not isinstance(data, bytes):
        raise TypeError("Canonical commit bundle data must be bytes.")
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanonicalCommitBundleError(
            "Invalid canonical commit bundle JSON."
        ) from exc
    if not isinstance(value, dict) or set(value) != {"body", "integrity"}:
        raise CanonicalCommitBundleError(
            "Invalid canonical commit bundle envelope."
        )
    body = value["body"]
    integrity = value["integrity"]
    if not isinstance(body, dict) or not isinstance(integrity, dict):
        raise CanonicalCommitBundleError(
            "Invalid canonical commit bundle envelope."
        )
    if set(body) != _BODY_KEYS:
        raise CanonicalCommitBundleError(
            "Invalid canonical commit bundle body."
        )
    if set(integrity) != {"algorithm", "body_sha256"}:
        raise CanonicalCommitBundleError(
            "Invalid canonical commit bundle integrity manifest."
        )
    if _canonical_bytes(value) != data:
        raise CanonicalCommitBundleError(
            "Bundle bytes are not canonical."
        )
    if body.get("format") != FORMAT or body.get("format_version") != FORMAT_VERSION:
        raise CanonicalCommitBundleError(
            "Unsupported canonical commit bundle format."
        )
    if integrity.get("algorithm") != "sha256":
        raise CanonicalCommitBundleError(
            "Unsupported integrity algorithm."
        )
    expected = hashlib.sha256(_canonical_bytes(body)).hexdigest()
    if integrity.get("body_sha256") != expected:
        raise CanonicalCommitBundleError(
            "Canonical commit bundle integrity mismatch."
        )

    raw_records = body["records"]
    if not isinstance(raw_records, list):
        raise CanonicalCommitBundleError(
            "Canonical commit bundle records must be an array."
        )
    records = tuple(
        _record_from_object(record, index)
        for index, record in enumerate(raw_records)
    )
    try:
        rebuilt = serialize_canonical_commit_bundle(
            commit_id=uuid.UUID(body["commit_id"]),
            commit_seq=body["commit_seq"],
            schema_version=body["schema_version"],
            previous_hash=body["previous_hash"],
            records=records,
        )
    except (CanonicalCommitBundleError, TypeError, ValueError) as exc:
        if isinstance(exc, CanonicalCommitBundleError):
            raise
        raise CanonicalCommitBundleError(
            "Invalid canonical commit bundle semantics."
        ) from exc
    if rebuilt.data != data:
        raise CanonicalCommitBundleError(
            "Bundle semantics are not in canonical order or representation."
        )
    return rebuilt
