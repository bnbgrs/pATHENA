"""Canonical request fingerprints for durable chat send operations."""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from dataclasses import dataclass
from enum import Enum

CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION = 1

JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class ChatSendMode(str, Enum):
    """Persistence-relevant chat execution modes."""

    DIRECT = "direct"
    GROUNDED = "grounded"


@dataclass(frozen=True, slots=True)
class ChatRequestFingerprint:
    """Canonical immutable identity for one complete chat-send request.

    Semantic checksum validation remains at the persistence boundary so corrupted
    durable rows are classified as ChatSendOperationSchemaError rather than leaking
    a lower-level value-object exception during reconstruction.
    """

    payload_json: str
    payload_sha256: str
    format_version: int

    def __post_init__(self) -> None:
        if not isinstance(self.payload_json, str):
            raise TypeError("Chat request fingerprint payload_json must be text.")
        if not isinstance(self.payload_sha256, str):
            raise TypeError("Chat request fingerprint payload_sha256 must be text.")
        if isinstance(self.format_version, bool) or not isinstance(self.format_version, int):
            raise TypeError("Chat request fingerprint format_version must be an integer.")


def _json_safe(value: object) -> JsonValue:
    """Convert supported nested values into a strict JSON representation."""

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                "Chat request fingerprint values must not contain NaN or infinity."
            )
        return value

    if isinstance(value, dict):
        result: dict[str, JsonValue] = {}

        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(
                    "Chat request fingerprint dictionaries require string keys."
                )

            result[key] = _json_safe(item)

        return result

    if isinstance(value, (list, tuple)):
        return [
            _json_safe(item)
            for item in value
        ]

    raise TypeError(
        "Unsupported chat request fingerprint value: "
        f"{type(value).__name__}."
    )


def _require_optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text or None.")
    return value


def _require_optional_positive_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer or None.")
    return value


def build_chat_request_fingerprint(
    *,
    mode: ChatSendMode,
    chat_id: uuid.UUID,
    content: str,
    requested_model_id: str | None,
    requested_embedding_model_id: str | None,
    effective_context_limit: int | None,
    max_output_tokens: int | None,
    temperature: float | None,
    reasoning_mode: str | None,
    retrieval_configuration: dict[str, object] | None = None,
) -> ChatRequestFingerprint:
    """Build one stable SHA-256 identity from all persistence-relevant inputs."""
    if not isinstance(mode, ChatSendMode):
        raise TypeError("Chat request fingerprint mode must be a ChatSendMode.")
    if not isinstance(chat_id, uuid.UUID):
        raise TypeError("Chat request fingerprint chat_id must be a UUID.")
    if not isinstance(content, str):
        raise TypeError("Chat request fingerprint content must be text.")
    validated_model_id = _require_optional_text(
        requested_model_id,
        "Chat request fingerprint requested_model_id",
    )
    validated_embedding_model_id = _require_optional_text(
        requested_embedding_model_id,
        "Chat request fingerprint requested_embedding_model_id",
    )
    validated_context_limit = _require_optional_positive_int(
        effective_context_limit,
        "Chat request fingerprint effective_context_limit",
    )
    validated_output_tokens = _require_optional_positive_int(
        max_output_tokens,
        "Chat request fingerprint max_output_tokens",
    )
    if temperature is not None:
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
            raise TypeError("Chat request fingerprint temperature must be numeric or None.")
        if not math.isfinite(float(temperature)):
            raise ValueError("Chat request fingerprint temperature must be finite.")
    validated_reasoning_mode = _require_optional_text(
        reasoning_mode,
        "Chat request fingerprint reasoning_mode",
    )
    if retrieval_configuration is not None and not isinstance(
        retrieval_configuration,
        dict,
    ):
        raise TypeError("Chat request fingerprint retrieval_configuration must be a dict or None.")

    retrieval = (
        {}
        if retrieval_configuration is None
        else retrieval_configuration
    )

    payload: dict[str, JsonValue] = {
        "fingerprint_format_version": (
            CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION
        ),
        "mode": mode.value,
        "chat_id": str(chat_id),
        "content": content,
        "requested_model_id": validated_model_id,
        "requested_embedding_model_id": (
            validated_embedding_model_id
        ),
        "effective_context_limit": validated_context_limit,
        "max_output_tokens": validated_output_tokens,
        "temperature": temperature,
        "reasoning_mode": validated_reasoning_mode,
        "retrieval_configuration": _json_safe(retrieval),
    }

    payload_json = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    payload_sha256 = hashlib.sha256(
        payload_json.encode("utf-8")
    ).hexdigest()

    return ChatRequestFingerprint(
        payload_json=payload_json,
        payload_sha256=payload_sha256,
        format_version=CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION,
    )
