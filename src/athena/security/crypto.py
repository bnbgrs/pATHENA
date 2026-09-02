"""Cryptographic primitives for ATHENA Protected Content.

No custom cryptographic primitive lives here. This module only provides a
small typed adapter around pyca/cryptography.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag, UnsupportedAlgorithm
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

from athena.security.models import Argon2idParameters

AES_256_GCM = "AES-256-GCM"
ARGON2ID = "argon2id"
KEY_BYTES = 32
NONCE_BYTES = 12
SALT_BYTES = 16


class CryptoProviderError(RuntimeError):
    """Base error for Protected-Content crypto adapter failures."""


class CryptoUnavailableError(
    CryptoProviderError
):
    """Raised when the configured cryptographic primitive is unavailable."""


class CryptoAuthenticationError(
    CryptoProviderError
):
    """Raised on authenticated-decryption failure."""


@dataclass(frozen=True, slots=True)
class AeadEnvelope:
    nonce: bytes
    ciphertext: bytes


def _require_bytes(value: object, label: str) -> bytes:
    if not isinstance(value, bytes):
        raise ValueError(f"{label} must be bytes.")
    return value


class CryptoProvider:
    """Thin adapter over Argon2id and AES-256-GCM."""

    def random_key(self) -> bytes:
        return secrets.token_bytes(
            KEY_BYTES
        )

    def random_nonce(self) -> bytes:
        return secrets.token_bytes(
            NONCE_BYTES
        )

    def random_salt(self) -> bytes:
        return secrets.token_bytes(
            SALT_BYTES
        )

    def derive_password_key(
        self,
        password: bytes,
        *,
        salt: bytes,
        parameters: Argon2idParameters,
    ) -> bytes:
        validated_password = _require_bytes(
            password,
            "Protected-Content password",
        )
        validated_salt = _require_bytes(
            salt,
            "Argon2id salt",
        )
        if not isinstance(parameters, Argon2idParameters):
            raise ValueError(
                "Argon2id parameters must be an Argon2idParameters value."
            )
        if not validated_password:
            raise ValueError(
                "Protected-Content password "
                "must not be empty."
            )

        if len(validated_salt) < SALT_BYTES:
            raise ValueError(
                "Argon2id salt must contain "
                "at least 16 bytes."
            )

        try:
            kdf = Argon2id(
                salt=validated_salt,
                length=parameters.length,
                iterations=(
                    parameters.iterations
                ),
                lanes=parameters.lanes,
                memory_cost=(
                    parameters.memory_cost_kib
                ),
            )

            return kdf.derive(
                validated_password
            )

        except UnsupportedAlgorithm as exc:
            raise CryptoUnavailableError(
                "Argon2id is unavailable in the active "
                "cryptography backend."
            ) from exc

        except MemoryError as exc:
            raise CryptoUnavailableError(
                "Insufficient memory for the configured "
                "Argon2id parameters."
            ) from exc

    def encrypt(
        self,
        key: bytes,
        plaintext: bytes,
        *,
        aad: bytes,
    ) -> AeadEnvelope:
        return self.encrypt_with_nonce(
            key,
            plaintext,
            nonce=self.random_nonce(),
            aad=aad,
        )

    def encrypt_with_nonce(
        self,
        key: bytes,
        plaintext: bytes,
        *,
        nonce: bytes,
        aad: bytes,
    ) -> AeadEnvelope:
        validated_key = self._require_aes256_key(
            key
        )
        validated_plaintext = _require_bytes(
            plaintext,
            "AES-256-GCM plaintext",
        )
        validated_nonce = _require_bytes(
            nonce,
            "AES-256-GCM nonce",
        )
        validated_aad = _require_bytes(
            aad,
            "AES-256-GCM AAD",
        )

        if len(validated_nonce) != NONCE_BYTES:
            raise ValueError(
                "AES-256-GCM nonces must contain exactly 12 bytes."
            )

        ciphertext = AESGCM(
            validated_key
        ).encrypt(
            validated_nonce,
            validated_plaintext,
            validated_aad,
        )

        return AeadEnvelope(
            nonce=validated_nonce,
            ciphertext=ciphertext,
        )

    def decrypt(
        self,
        key: bytes,
        *,
        nonce: bytes,
        ciphertext: bytes,
        aad: bytes,
    ) -> bytes:
        validated_key = self._require_aes256_key(
            key
        )
        if (
            not isinstance(nonce, bytes)
            or len(nonce) != NONCE_BYTES
            or not isinstance(ciphertext, bytes)
            or not isinstance(aad, bytes)
        ):
            raise CryptoAuthenticationError(
                "Protected-Content authentication failed."
            )

        try:
            return AESGCM(
                validated_key
            ).decrypt(
                nonce,
                ciphertext,
                aad,
            )

        except (InvalidTag, ValueError, TypeError) as exc:
            raise CryptoAuthenticationError(
                "Protected-Content authentication failed."
            ) from exc

    @staticmethod
    def ciphertext_hash(
        ciphertext: bytes,
    ) -> bytes:
        validated = _require_bytes(
            ciphertext,
            "Ciphertext",
        )
        return hashlib.sha256(
            validated
        ).digest()

    @staticmethod
    def _require_aes256_key(
        key: bytes,
    ) -> bytes:
        validated = _require_bytes(
            key,
            "AES-256-GCM key",
        )
        if len(validated) != KEY_BYTES:
            raise ValueError(
                "AES-256-GCM keys must contain "
                "exactly 32 bytes."
            )
        return validated
