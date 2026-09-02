from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid

import pytest

from athena.chat.grounded_receipt import (
    GROUNDED_RESPONSE_RECEIPT_FORMAT_VERSION,
    GroundedResponseReceipt,
    GroundedResponseReceiptCorruptionError,
    _canonical_payload,
    _receipt_from_row,
)


@pytest.mark.parametrize("value", [None, b"{}", 1, True, object()])
def test_canonical_receipt_payload_requires_text(value: object) -> None:
    with pytest.raises(ValueError, match="payload must be JSON text"):
        _canonical_payload(value)  # type: ignore[arg-type]


def test_receipt_value_rejects_noncanonical_digest() -> None:
    with pytest.raises(ValueError, match="canonical lowercase SHA-256"):
        GroundedResponseReceipt(
            operation_id=uuid.uuid4(),
            chat_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            payload_json="{}",
            payload_sha256="A" * 64,
            format_version=GROUNDED_RESPONSE_RECEIPT_FORMAT_VERSION,
            created_at_us=1,
        )


@pytest.mark.parametrize("created_at_us", [True, False, -1, 1.5, "1"])
def test_receipt_value_rejects_invalid_created_timestamp(created_at_us: object) -> None:
    digest = hashlib.sha256(b"{}").hexdigest()
    with pytest.raises((TypeError, ValueError)):
        GroundedResponseReceipt(
            operation_id=uuid.uuid4(),
            chat_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            payload_json="{}",
            payload_sha256=digest,
            format_version=GROUNDED_RESPONSE_RECEIPT_FORMAT_VERSION,
            created_at_us=created_at_us,  # type: ignore[arg-type]
        )


def test_persisted_invalid_timestamp_is_classified_as_corruption() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    canonical = json.dumps({}, separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    row = connection.execute(
        "SELECT ? AS operation_id, ? AS chat_id, ? AS processing_run_id, "
        "? AS payload_json, ? AS payload_sha256, ? AS format_version, ? AS created_at_us",
        (
            uuid.uuid4().bytes,
            uuid.uuid4().bytes,
            uuid.uuid4().bytes,
            canonical,
            digest,
            GROUNDED_RESPONSE_RECEIPT_FORMAT_VERSION,
            -1,
        ),
    ).fetchone()
    assert row is not None

    with pytest.raises(GroundedResponseReceiptCorruptionError, match="invalid persisted fields"):
        _receipt_from_row(row)

    connection.close()
