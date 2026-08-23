from __future__ import annotations

import uuid

import pytest

from athena.backup.deletion_codec import DeletionLedgerCodecMixin
from athena.backup.errors import BackupRestoreError


class _Codec(DeletionLedgerCodecMixin):
    DELETION_LEDGER_RECORD_FORMAT_VERSION = 1
    DELETION_LEDGER_HEAD_FORMAT_VERSION = 1


def _payload(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "deleted_at_us": 123,
        "deleted_by_actor_id": str(uuid.uuid4()),
        "deletion_commit_seq": 7,
        "deletion_id": str(uuid.uuid4()),
        "entity_id": str(uuid.uuid4()),
        "entity_type": "source",
        "format_version": 1,
        "ledger_seq": 3,
    }
    values.update(overrides)
    return values


@pytest.mark.parametrize(
    "field",
    ["deleted_at_us", "deletion_commit_seq", "ledger_seq"],
)
def test_deletion_ledger_decoder_rejects_integers_above_sqlite_range(
    field: str,
) -> None:
    with pytest.raises(BackupRestoreError, match=field):
        _Codec._deletion_record_from_payload(
            _payload(**{field: 1 << 63})
        )


def test_deletion_ledger_decoder_accepts_signed_int64_maximum() -> None:
    maximum = (1 << 63) - 1

    record = _Codec._deletion_record_from_payload(
        _payload(
            deleted_at_us=maximum,
            deletion_commit_seq=maximum,
            ledger_seq=maximum,
        )
    )

    assert record.deleted_at_us == maximum
    assert record.deletion_commit_seq == maximum
    assert record.ledger_seq == maximum
