from __future__ import annotations

import json
import uuid

import pytest

from athena.chat.request_fingerprint import (
    ChatSendMode,
    build_chat_request_fingerprint,
)

CHAT_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _fingerprint(
    *,
    content: str = "same words",
    retrieval: dict[str, object] | None = None,
):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=CHAT_ID,
        content=content,
        requested_model_id="local-model",
        requested_embedding_model_id="embedding-model",
        effective_context_limit=8192,
        max_output_tokens=2048,
        temperature=0.4,
        reasoning_mode="off",
        retrieval_configuration=retrieval,
    )


def test_request_fingerprint_is_canonical_and_binds_exact_content() -> None:
    first = _fingerprint(retrieval={"b": 2, "a": 1})
    reordered = _fingerprint(retrieval={"a": 1, "b": 2})
    changed = _fingerprint(
        content=" same words ",
        retrieval={"a": 1, "b": 2},
    )

    assert first == reordered
    assert first.payload_sha256 != changed.payload_sha256
    assert len(first.payload_sha256) == 64
    payload = json.loads(first.payload_json)
    assert payload["mode"] == "grounded"
    assert payload["chat_id"] == str(CHAT_ID)
    assert payload["content"] == "same words"
    assert payload["retrieval_configuration"] == {"a": 1, "b": 2}


def test_request_fingerprint_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError, match="NaN or infinity"):
        _fingerprint(retrieval={"score": float("nan")})
