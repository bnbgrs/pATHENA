from __future__ import annotations

import hashlib
import json
import uuid

import pytest

from athena.storage.canonical_commit_bundle import (
    MAX_SAFE_INTEGER,
    CanonicalCommitBundleError,
    CanonicalCommitRecord,
    serialize_canonical_commit_bundle,
    verify_canonical_commit_bundle,
)


def _record(
    record_id: str,
    *,
    record_type: str = "claim_revision",
    metadata: dict[str, object] | None = None,
    payload: object = None,
    payload_kind: str = "json",
    protected: bool = False,
) -> CanonicalCommitRecord:
    return CanonicalCommitRecord(
        record_type=record_type,
        record_id=record_id,
        schema_version=1,
        metadata={} if metadata is None else metadata,
        payload={} if payload is None else payload,
        payload_kind=payload_kind,
        protected=protected,
    )


def _serialize(
    records: list[CanonicalCommitRecord],
    *,
    previous_hash: str | None = "AB" * 32,
):
    return serialize_canonical_commit_bundle(
        commit_id=uuid.UUID("018f0000-0000-7000-8000-000000000001"),
        commit_seq=7,
        schema_version=41,
        previous_hash=previous_hash,
        records=records,
    )


def _ascii_canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def test_bundle_bytes_and_hash_are_stable_across_record_input_order() -> None:
    first = _record("b", metadata={"state": "active"}, payload={"value": 2})
    second = _record("a", metadata={"state": "active"}, payload={"value": 1})

    left = _serialize([first, second])
    right = _serialize([second, first])

    assert left == right
    assert hashlib.sha256(left.data).hexdigest() == left.bundle_hash
    assert verify_canonical_commit_bundle(left.data) == left

    decoded = json.loads(left.data)
    assert [row["record_id"] for row in decoded["body"]["records"]] == ["a", "b"]
    assert decoded["body"]["previous_hash"] == "ab" * 32


def test_rfc8785_property_order_uses_utf16_code_units() -> None:
    # U+1F600 starts with UTF-16 code unit D83D, which sorts before U+E000.
    # Python code-point sorting would produce the opposite order.
    emoji = "\U0001f600"
    private_use = "\ue000"
    bundle = _serialize(
        [
            _record(
                "unicode",
                metadata={private_use: 1, emoji: 2},
                payload={"ok": True},
            )
        ]
    )

    text = bundle.data.decode("utf-8")
    assert text.index(f'"{emoji}"') < text.index(f'"{private_use}"')
    assert verify_canonical_commit_bundle(bundle.data) == bundle


@pytest.mark.parametrize(
    "value",
    [
        1.25,
        float("nan"),
        float("inf"),
        MAX_SAFE_INTEGER + 1,
        -(MAX_SAFE_INTEGER + 1),
    ],
)
def test_noncanonical_number_domain_is_rejected(value: object) -> None:
    with pytest.raises(CanonicalCommitBundleError):
        _serialize([_record("numbers", payload={"value": value})])


def test_duplicate_record_identity_is_rejected() -> None:
    with pytest.raises(
        CanonicalCommitBundleError,
        match="Duplicate canonical record identity",
    ):
        _serialize([_record("same"), _record("same")])


def test_protected_record_cannot_materialize_plaintext_json_payload() -> None:
    with pytest.raises(
        CanonicalCommitBundleError,
        match="Protected records may not materialize plaintext JSON",
    ):
        _serialize(
            [
                _record(
                    "protected",
                    protected=True,
                    payload_kind="json",
                    payload={"secret": "canary-secret"},
                )
            ]
        )


@pytest.mark.parametrize("payload_kind", ["ciphertext", "protected_ref"])
def test_protected_record_accepts_opaque_representation_kinds(
    payload_kind: str,
) -> None:
    bundle = _serialize(
        [
            _record(
                "protected",
                protected=True,
                payload_kind=payload_kind,
                metadata={"protection_scope_id": "scope-1"},
                payload={"opaque": "payload-ref"},
            )
        ]
    )

    assert verify_canonical_commit_bundle(bundle.data) == bundle


def test_noncanonical_whitespace_is_rejected_even_when_json_is_equivalent() -> None:
    bundle = _serialize([_record("a")])
    equivalent = json.dumps(
        json.loads(bundle.data),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ).encode("utf-8")

    with pytest.raises(CanonicalCommitBundleError, match="not canonical"):
        verify_canonical_commit_bundle(equivalent)


def test_body_tamper_is_rejected_by_integrity_manifest() -> None:
    bundle = _serialize([_record("a")])
    value = json.loads(bundle.data)
    value["body"]["commit_seq"] = 8
    tampered = _ascii_canonical(value)

    with pytest.raises(CanonicalCommitBundleError, match="integrity mismatch"):
        verify_canonical_commit_bundle(tampered)


def test_rehashed_semantically_invalid_body_is_still_rejected() -> None:
    bundle = _serialize([_record("a")])
    value = json.loads(bundle.data)
    value["body"]["commit_seq"] = 0
    value["integrity"]["body_sha256"] = hashlib.sha256(
        _ascii_canonical(value["body"])
    ).hexdigest()
    invalid = _ascii_canonical(value)

    with pytest.raises(CanonicalCommitBundleError, match="positive RFC 8785 safe integer"):
        verify_canonical_commit_bundle(invalid)


def test_rehashed_protected_plaintext_record_is_still_rejected() -> None:
    bundle = _serialize(
        [
            _record(
                "protected",
                protected=True,
                payload_kind="protected_ref",
                payload={"opaque": "ref"},
            )
        ]
    )
    value = json.loads(bundle.data)
    record = value["body"]["records"][0]
    record["payload_kind"] = "json"
    record["payload"] = {"secret": "canary-secret"}
    value["integrity"]["body_sha256"] = hashlib.sha256(
        _ascii_canonical(value["body"])
    ).hexdigest()
    invalid = _ascii_canonical(value)

    with pytest.raises(
        CanonicalCommitBundleError,
        match="Protected records may not materialize plaintext JSON",
    ):
        verify_canonical_commit_bundle(invalid)


def test_extra_envelope_fields_are_rejected() -> None:
    bundle = _serialize([_record("a")])
    value = json.loads(bundle.data)
    value["unexpected"] = True

    with pytest.raises(CanonicalCommitBundleError, match="Invalid canonical commit bundle envelope"):
        verify_canonical_commit_bundle(_ascii_canonical(value))


def test_invalid_unicode_scalar_is_rejected() -> None:
    with pytest.raises(CanonicalCommitBundleError, match="Invalid Unicode scalar"):
        _serialize([_record("bad-surrogate", metadata={"bad": "\ud800"})])


def test_commit_id_requires_canonical_uuid_type() -> None:
    with pytest.raises(CanonicalCommitBundleError, match="commit_id must be a UUID"):
        serialize_canonical_commit_bundle(
            commit_id="018f0000-0000-7000-8000-000000000001",  # type: ignore[arg-type]
            commit_seq=7,
            schema_version=41,
            previous_hash=None,
            records=[_record("a")],
        )


def test_invalid_previous_hash_is_rejected() -> None:
    with pytest.raises(CanonicalCommitBundleError, match="previous_hash"):
        _serialize([_record("a")], previous_hash="not-a-hash")
