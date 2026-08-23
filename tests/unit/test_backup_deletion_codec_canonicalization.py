from __future__ import annotations

import copy

import pytest

from athena.backup import service


VALID = {
    "deleted_at_us": 123456789,
    "deleted_by_actor_id": "00000000-0000-7000-8000-000000000201",
    "deletion_commit_seq": 11,
    "deletion_id": "00000000-0000-7000-8000-000000000001",
    "entity_id": "00000000-0000-7000-8000-000000000101",
    "entity_type": "personal_memory",
    "format_version": 1,
    "ledger_seq": 1,
}


@pytest.mark.parametrize(
    "field,value",
    [
        pytest.param(
            "deletion_id",
            "00000000-0000-7000-8000-00000000000A",
            id="uuid-uppercase",
        ),
        pytest.param(
            "entity_id",
            "{00000000-0000-7000-8000-000000000101}",
            id="uuid-braces",
        ),
        pytest.param(
            "deleted_by_actor_id",
            " 00000000-0000-7000-8000-000000000201",
            id="uuid-leading-space",
        ),
        pytest.param(
            "deletion_id",
            12345678901234567890123456789012,
            id="uuid-integer",
        ),
        pytest.param(
            "entity_id",
            None,
            id="uuid-none",
        ),
        pytest.param(
            "entity_type",
            " personal_memory",
            id="entity-type-leading-space",
        ),
        pytest.param(
            "entity_type",
            "personal_memory ",
            id="entity-type-trailing-space",
        ),
        pytest.param(
            "entity_type",
            "",
            id="entity-type-empty",
        ),
    ],
)
def test_deletion_record_decoder_rejects_noncanonical_identity_fields(
    field: str,
    value: object,
) -> None:
    payload = copy.deepcopy(VALID)
    payload[field] = value

    with pytest.raises(service.BackupRestoreError):
        service.BackupService._deletion_record_from_payload(payload)


@pytest.mark.parametrize(
    "field,value",
    [
        pytest.param("ledger_seq", True, id="ledger-bool"),
        pytest.param("ledger_seq", 0, id="ledger-zero"),
        pytest.param("deleted_at_us", False, id="deleted-at-bool"),
        pytest.param("deleted_at_us", -1, id="deleted-at-negative"),
        pytest.param("deletion_commit_seq", True, id="commit-bool"),
        pytest.param("deletion_commit_seq", 0, id="commit-zero"),
        pytest.param("format_version", True, id="format-bool"),
    ],
)
def test_deletion_record_decoder_keeps_integer_fields_bool_safe(
    field: str,
    value: object,
) -> None:
    payload = copy.deepcopy(VALID)
    payload[field] = value

    with pytest.raises(service.BackupRestoreError):
        service.BackupService._deletion_record_from_payload(payload)


def test_deletion_record_decoder_roundtrips_canonical_payload() -> None:
    record = service.BackupService._deletion_record_from_payload(copy.deepcopy(VALID))

    assert service.BackupService._deletion_record_payload(record) == VALID
