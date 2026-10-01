from __future__ import annotations

import uuid

import pytest

from athena.security.crypto import AES_256_GCM
from athena.security.models import (
    KeyStatus,
    ProtectedPayloadRecord,
    ProtectionScopeKeyRecord,
    ProtectionScopeLifecycle,
    ProtectionScopeRecord,
)
from athena.security.repository import (
    ProtectionRepository,
    ProtectionRepositoryIntegrityError,
)
from athena.storage.database import SQLiteDatabase


def _repository_with_scope(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    repository = ProtectionRepository(database)

    scope_id = uuid.uuid4()
    scope_key_id = uuid.uuid4()
    scope = ProtectionScopeRecord(
        protection_scope_id=scope_id,
        lifecycle_state=ProtectionScopeLifecycle.ACTIVE,
        created_at_us=1,
        current_scope_key_id=scope_key_id,
        neutral_label=None,
    )
    scope_key = ProtectionScopeKeyRecord(
        scope_key_id=scope_key_id,
        protection_scope_id=scope_id,
        key_version=1,
        wrap_algorithm=AES_256_GCM,
        wrap_nonce=b"n" * 12,
        wrapped_scope_key=b"k" * 48,
        created_at_us=1,
        retired_at_us=None,
        status=KeyStatus.ACTIVE,
    )
    repository.create_scope_with_key(scope, scope_key)
    return database, repository, scope_id, scope_key_id


def test_scope_key_reader_rejects_text_nonce_even_when_length_check_passes(
    tmp_path,
) -> None:
    database, repository, scope_id, scope_key_id = _repository_with_scope(tmp_path)
    try:
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE protection_scope_keys
                SET wrap_nonce = ?
                WHERE scope_key_id = ?
                """,
                ("n" * 12, scope_key_id.bytes),
            )

        with pytest.raises(
            ProtectionRepositoryIntegrityError,
            match="persisted type",
        ):
            repository.get_current_scope_key(scope_id)
    finally:
        database.stop()


def test_payload_reader_rejects_text_nonce_even_when_length_check_passes(
    tmp_path,
) -> None:
    database, repository, scope_id, scope_key_id = _repository_with_scope(tmp_path)
    try:
        payload_id = uuid.uuid4()
        repository.insert_payload(
            ProtectedPayloadRecord(
                protected_payload_id=payload_id,
                protection_scope_id=scope_id,
                scope_key_id=scope_key_id,
                cipher_suite=AES_256_GCM,
                ciphertext=b"c" * 16,
                nonce=b"n" * 12,
                wrapped_dek=b"d" * 48,
                dek_wrap_nonce=b"w" * 12,
                aad_version=1,
                ciphertext_hash=b"h" * 32,
                created_at_us=2,
            )
        )

        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE protected_payloads
                SET nonce = ?
                WHERE protected_payload_id = ?
                """,
                ("n" * 12, payload_id.bytes),
            )

        with pytest.raises(
            ProtectionRepositoryIntegrityError,
            match="persisted type",
        ):
            repository.get_payload(payload_id)
    finally:
        database.stop()
