from __future__ import annotations

from typing import Any

import pytest

from athena.security.crypto import (
    CryptoAuthenticationError,
    CryptoProvider,
)
from athena.security.models import Argon2idParameters


@pytest.fixture
def crypto() -> CryptoProvider:
    return CryptoProvider()


@pytest.mark.parametrize("password", ["secret", bytearray(b"secret"), None])
def test_password_derivation_requires_bytes(
    crypto: CryptoProvider,
    password: Any,
) -> None:
    with pytest.raises(ValueError):
        crypto.derive_password_key(
            password,
            salt=b"s" * 16,
            parameters=Argon2idParameters(),
        )


@pytest.mark.parametrize("salt", ["s" * 16, bytearray(b"s" * 16), None])
def test_password_derivation_requires_byte_salt(
    crypto: CryptoProvider,
    salt: Any,
) -> None:
    with pytest.raises(ValueError):
        crypto.derive_password_key(
            b"secret",
            salt=salt,
            parameters=Argon2idParameters(),
        )


def test_password_derivation_requires_parameter_object(
    crypto: CryptoProvider,
) -> None:
    with pytest.raises(ValueError):
        crypto.derive_password_key(
            b"secret",
            salt=b"s" * 16,
            parameters={"iterations": 3},  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("key", "k" * 32),
        ("key", bytearray(b"k" * 32)),
        ("plaintext", "plaintext"),
        ("plaintext", bytearray(b"plaintext")),
        ("nonce", "n" * 12),
        ("nonce", bytearray(b"n" * 12)),
        ("aad", "aad"),
        ("aad", bytearray(b"aad")),
    ],
)
def test_encrypt_with_nonce_requires_exact_bytes(
    crypto: CryptoProvider,
    field: str,
    value: Any,
) -> None:
    kwargs: dict[str, Any] = {
        "key": b"k" * 32,
        "plaintext": b"plaintext",
        "nonce": b"n" * 12,
        "aad": b"aad",
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        crypto.encrypt_with_nonce(**kwargs)


@pytest.mark.parametrize(
    "field,value",
    [
        ("nonce", b"short"),
        ("nonce", "n" * 12),
        ("ciphertext", "ciphertext"),
        ("ciphertext", bytearray(b"ciphertext")),
        ("aad", "aad"),
        ("aad", bytearray(b"aad")),
    ],
)
def test_decrypt_malformed_authentication_inputs_share_generic_error(
    crypto: CryptoProvider,
    field: str,
    value: Any,
) -> None:
    kwargs: dict[str, Any] = {
        "key": b"k" * 32,
        "nonce": b"n" * 12,
        "ciphertext": b"ciphertext",
        "aad": b"aad",
    }
    kwargs[field] = value

    with pytest.raises(
        CryptoAuthenticationError,
        match="Protected-Content authentication failed",
    ):
        crypto.decrypt(**kwargs)


def test_encrypt_decrypt_roundtrip_remains_valid(
    crypto: CryptoProvider,
) -> None:
    key = b"k" * 32
    envelope = crypto.encrypt_with_nonce(
        key,
        b"plaintext",
        nonce=b"n" * 12,
        aad=b"aad",
    )

    assert crypto.decrypt(
        key,
        nonce=envelope.nonce,
        ciphertext=envelope.ciphertext,
        aad=b"aad",
    ) == b"plaintext"


def test_ciphertext_hash_requires_bytes(crypto: CryptoProvider) -> None:
    with pytest.raises(ValueError):
        crypto.ciphertext_hash(bytearray(b"ciphertext"))  # type: ignore[arg-type]
