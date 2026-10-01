"""Canonical deterministic commit bundles for structured replication."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

FORMAT = "athena.canonical-commit-bundle"
FORMAT_VERSION = 1
_ALLOWED_PAYLOAD_KINDS = frozenset({"json", "ciphertext", "protected_ref"})


class CanonicalCommitBundleError(ValueError):
    """Raised when a replication bundle violates the canonical contract."""


@dataclass(frozen=True, slots=True)
class CanonicalCommitRecord:
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


def _require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CanonicalCommitBundleError(f"{name} must be non-empty text.")
    return value


def _hash(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise CanonicalCommitBundleError("previous_hash must contain 64 hex characters.")
    normalized = value.lower()
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        raise CanonicalCommitBundleError(
            "previous_hash must contain 64 hex characters."
        ) from exc
    return normalized


def _validate_json(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise CanonicalCommitBundleError(f"Floating-point values are forbidden at {path}.")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalCommitBundleError(f"Object keys must be strings at {path}.")
            _validate_json(item, f"{path}.{key}")
        return
    raise CanonicalCommitBundleError(f"Unsupported canonical JSON value at {path}.")


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    _validate_json(dict(value))
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _record_object(record: CanonicalCommitRecord) -> dict[str, Any]:
    record_type = _require_text(record.record_type, "record_type")
    record_id = _require_text(record.record_id, "record_id")
    if (
        isinstance(record.schema_version, bool)
        or not isinstance(record.schema_version, int)
        or record.schema_version < 1
    ):
        raise CanonicalCommitBundleError("schema_version must be a positive integer.")
    if record.payload_kind not in _ALLOWED_PAYLOAD_KINDS:
        raise CanonicalCommitBundleError("Unsupported payload_kind.")
    if record.protected and record.payload_kind == "json":
        raise CanonicalCommitBundleError(
            "Protected records may not materialize plaintext JSON payloads."
        )
    metadata = dict(record.metadata)
    _validate_json(metadata, "$.metadata")
    _validate_json(record.payload, "$.payload")
    return {
        "metadata": metadata,
        "payload": record.payload,
        "payload_kind": record.payload_kind,
        "protected": record.protected,
        "record_id": record_id,
        "record_type": record_type,
        "schema_version": record.schema_version,
    }


def serialize_canonical_commit_bundle(
    *,
    commit_id: str,
    commit_seq: int,
    schema_version: int,
    previous_hash: str | None,
    records: Sequence[CanonicalCommitRecord],
) -> CanonicalCommitBundle:
    """Serialize already-selected replication records without reading storage."""
    identifier = _require_text(commit_id, "commit_id")
    for name, value in (("commit_seq", commit_seq), ("schema_version", schema_version)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise CanonicalCommitBundleError(f"{name} must be a positive integer.")

    keyed: list[tuple[tuple[str, str, int], dict[str, Any]]] = []
    seen: set[tuple[str, str, int]] = set()
    for record in records:
        obj = _record_object(record)
        key = (record.record_type, record.record_id, record.schema_version)
        if key in seen:
            raise CanonicalCommitBundleError("Duplicate canonical record identity.")
        seen.add(key)
        keyed.append((key, obj))
    keyed.sort(key=lambda item: item[0])

    body: dict[str, Any] = {
        "commit_id": identifier,
        "commit_seq": commit_seq,
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "previous_hash": _hash(previous_hash),
        "records": [obj for _, obj in keyed],
        "schema_version": schema_version,
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
    return CanonicalCommitBundle(data=data, bundle_hash=hashlib.sha256(data).hexdigest())


def verify_canonical_commit_bundle(data: bytes) -> CanonicalCommitBundle:
    """Verify integrity and require the exact canonical byte representation."""
    if not isinstance(data, bytes):
        raise TypeError("Canonical commit bundle data must be bytes.")
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanonicalCommitBundleError("Invalid canonical commit bundle JSON.") from exc
    if not isinstance(value, dict) or set(value) != {"body", "integrity"}:
        raise CanonicalCommitBundleError("Invalid canonical commit bundle envelope.")
    body = value["body"]
    integrity = value["integrity"]
    if not isinstance(body, dict) or not isinstance(integrity, dict):
        raise CanonicalCommitBundleError("Invalid canonical commit bundle envelope.")
    if _canonical_bytes(value) != data:
        raise CanonicalCommitBundleError("Bundle bytes are not canonical.")
    if body.get("format") != FORMAT or body.get("format_version") != FORMAT_VERSION:
        raise CanonicalCommitBundleError("Unsupported canonical commit bundle format.")
    if integrity.get("algorithm") != "sha256":
        raise CanonicalCommitBundleError("Unsupported integrity algorithm.")
    expected = hashlib.sha256(_canonical_bytes(body)).hexdigest()
    if integrity.get("body_sha256") != expected:
        raise CanonicalCommitBundleError("Canonical commit bundle integrity mismatch.")
    return CanonicalCommitBundle(data=data, bundle_hash=hashlib.sha256(data).hexdigest())
