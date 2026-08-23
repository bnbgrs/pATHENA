"""Runtime and persistence models for ATHENA Protected Content."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Self, cast


class ProtectionScopeLifecycle(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"
    PENDING_DELETE = "pending_delete"


class KeySlotType(str, Enum):
    PASSWORD = "password"
    RECOVERY = "recovery"
    OS_SECRET = "os_secret"


class KeyStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"


def _required_exact_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Argon2id parameter {name!r} must be an integer.")
    return value


@dataclass(frozen=True, slots=True)
class Argon2idParameters:
    """Versioned Argon2id profile persisted with a password key slot."""

    format_version: int = 1
    iterations: int = 3
    lanes: int = 4
    memory_cost_kib: int = 64 * 1024
    length: int = 32

    def __post_init__(self) -> None:
        format_version = _required_exact_int(self.format_version, "format_version")
        iterations = _required_exact_int(self.iterations, "iterations")
        lanes = _required_exact_int(self.lanes, "lanes")
        memory_cost_kib = _required_exact_int(self.memory_cost_kib, "memory_cost_kib")
        length = _required_exact_int(self.length, "length")

        if format_version != 1:
            raise ValueError(
                "Unsupported Argon2id parameter format."
            )

        if iterations < 1:
            raise ValueError(
                "Argon2id iterations must be positive."
            )

        if lanes < 1:
            raise ValueError(
                "Argon2id lanes must be positive."
            )

        if memory_cost_kib < 8 * lanes:
            raise ValueError(
                "Argon2id memory_cost_kib is too small "
                "for the lane count."
            )

        if length != 32:
            raise ValueError(
                "ATHENA password KEKs must be "
                "exactly 32 bytes."
            )

    def to_json(self) -> str:
        return json.dumps(
            {
                "format_version": (
                    self.format_version
                ),
                "iterations": self.iterations,
                "lanes": self.lanes,
                "length": self.length,
                "memory_cost_kib": (
                    self.memory_cost_kib
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> Self:
        if not isinstance(value, str):
            raise ValueError(
                "Argon2id parameter JSON must be text."
            )
        try:
            parsed: object = json.loads(
                value
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid Argon2id parameter JSON."
            ) from exc

        if not isinstance(
            parsed,
            dict,
        ):
            raise ValueError(
                "Argon2id parameter JSON "
                "must be an object."
            )

        data = cast(
            dict[str, object],
            parsed,
        )
        expected_keys = {
            "format_version",
            "iterations",
            "lanes",
            "length",
            "memory_cost_kib",
        }
        if set(data) != expected_keys:
            raise ValueError(
                "Argon2id parameter JSON has unexpected or missing fields."
            )

        return cls(
            format_version=_required_exact_int(
                data["format_version"],
                "format_version",
            ),
            iterations=_required_exact_int(
                data["iterations"],
                "iterations",
            ),
            lanes=_required_exact_int(
                data["lanes"],
                "lanes",
            ),
            memory_cost_kib=_required_exact_int(
                data["memory_cost_kib"],
                "memory_cost_kib",
            ),
            length=_required_exact_int(
                data["length"],
                "length",
            ),
        )


DEFAULT_ARGON2ID_PARAMETERS = (
    Argon2idParameters()
)


@dataclass(frozen=True, slots=True)
class PasswordKeySlotRecord:
    key_slot_id: uuid.UUID
    slot_type: KeySlotType
    kdf_algorithm: str
    kdf_parameters: Argon2idParameters
    salt: bytes
    wrap_algorithm: str
    wrap_nonce: bytes
    wrapped_root_key: bytes
    created_at_us: int
    retired_at_us: int | None
    status: KeyStatus


@dataclass(frozen=True, slots=True)
class ProtectionScopeRecord:
    protection_scope_id: uuid.UUID
    lifecycle_state: ProtectionScopeLifecycle
    created_at_us: int
    current_scope_key_id: uuid.UUID | None
    neutral_label: str | None


@dataclass(frozen=True, slots=True)
class ProtectionScopeKeyRecord:
    scope_key_id: uuid.UUID
    protection_scope_id: uuid.UUID
    key_version: int
    wrap_algorithm: str
    wrap_nonce: bytes
    wrapped_scope_key: bytes
    created_at_us: int
    retired_at_us: int | None
    status: KeyStatus


@dataclass(frozen=True, slots=True)
class ProtectedPayloadRecord:
    protected_payload_id: uuid.UUID
    protection_scope_id: uuid.UUID
    scope_key_id: uuid.UUID
    cipher_suite: str
    ciphertext: bytes
    nonce: bytes
    wrapped_dek: bytes
    dek_wrap_nonce: bytes
    aad_version: int
    ciphertext_hash: bytes
    created_at_us: int


@dataclass(frozen=True, slots=True)
class ProtectedBlobEnvelopeRecord:
    blob_id: uuid.UUID
    protection_scope_id: uuid.UUID
    scope_key_id: uuid.UUID
    wrapped_dek: bytes
    dek_wrap_nonce: bytes
    nonce_prefix: bytes
    chunk_size: int
    cipher_suite: str
    format_version: int


@dataclass(frozen=True, slots=True)
class SecurityContext:
    """Runtime-only authorization view. It is never persisted."""

    unlocked_protection_scopes: (
        frozenset[uuid.UUID]
    )

    def allows(
        self,
        protection_scope_id: uuid.UUID,
    ) -> bool:
        return (
            protection_scope_id
            in self.unlocked_protection_scopes
        )
