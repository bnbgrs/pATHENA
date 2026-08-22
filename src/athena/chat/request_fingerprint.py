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
    """Canonical immutable identity for one complete chat-send request."""

    payload_json: str
    payload_sha256: str
    format_version: int


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
        "requested_model_id": requested_model_id,
        "requested_embedding_model_id": (
            requested_embedding_model_id
        ),
        "effective_context_limit": effective_context_limit,
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
        "reasoning_mode": reasoning_mode,
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
