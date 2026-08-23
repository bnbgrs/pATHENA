from __future__ import annotations

import json
import uuid

import pytest

from athena.chat.request_fingerprint import (
    CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION,
    ChatRequestFingerprint,
    ChatSendMode,
    build_chat_request_fingerprint,
)


def _build(**overrides: object) -> ChatRequestFingerprint:
    values: dict[str, object] = {
        "mode": ChatSendMode.GROUNDED,
        "chat_id": uuid.uuid4(),
        "content": "hello",
        "requested_model_id": None,
        "requested_embedding_model_id": None,
        "effective_context_limit": None,
        "max_output_tokens": None,
        "temperature": None,
        "reasoning_mode": None,
        "retrieval_configuration": None,
    }
    values.update(overrides)
    return build_chat_request_fingerprint(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["effective_context_limit", "max_output_tokens"])
@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "10"])
def test_fingerprint_rejects_invalid_positive_integer_controls(
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValueError):
        _build(**{field: value})


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), float("-inf")])
def test_fingerprint_rejects_invalid_temperature(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _build(temperature=value)


def test_fingerprint_rejects_tampered_checksum() -> None:
    payload = json.dumps(
        {"fingerprint_format_version": CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION},
        sort_keys=True,
        separators=(",", ":"),
    )
    with pytest.raises(ValueError, match="checksum"):
        ChatRequestFingerprint(
            payload_json=payload,
            payload_sha256="0" * 64,
            format_version=CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION,
        )


def test_fingerprint_rejects_noncanonical_payload_json() -> None:
    payload = '{"b":2, "a":1}'
    with pytest.raises(ValueError, match="canonical JSON"):
        ChatRequestFingerprint(
            payload_json=payload,
            payload_sha256="0" * 64,
            format_version=CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION,
        )


def test_builder_returns_self_verifying_fingerprint() -> None:
    fingerprint = _build(effective_context_limit=4096, max_output_tokens=512)

    assert ChatRequestFingerprint(
        payload_json=fingerprint.payload_json,
        payload_sha256=fingerprint.payload_sha256,
        format_version=fingerprint.format_version,
    ) == fingerprint
