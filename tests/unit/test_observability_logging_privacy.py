from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping

from athena.observability.logging import JsonFormatter


def _format_record(
    message: object,
    *,
    args: tuple[object, ...] | Mapping[str, object] = (),
    extra: dict[str, object] | None = None,
    exc_info: tuple[type[BaseException], BaseException, object] | None = None,
) -> tuple[str, dict[str, object]]:
    record = logging.LogRecord(
        "athena.test",
        logging.INFO,
        __file__,
        10,
        message,
        args,
        exc_info,
    )
    if extra is not None:
        record.__dict__.update(extra)
    encoded = JsonFormatter().format(record)
    return encoded, json.loads(encoded)


def test_json_formatter_redacts_secrets_in_message_and_url_query() -> None:
    encoded, payload = _format_record(
        "POST https://example.test/v1?api_key=sekret&mode=fast "
        "Authorization: Bearer abc123"
    )

    assert "sekret" not in encoded
    assert "abc123" not in encoded
    assert "mode=fast" in str(payload["message"])
    assert "REDACTED" in str(payload["message"])


def test_json_formatter_redacts_oauth_query_values_and_drops_fragments() -> None:
    encoded, payload = _format_record(
        "GET https://example.test/callback?code=oauth-code&state=oauth-state"
        "&key=oauth-key&nonce=oauth-nonce&mode=safe#access_token=fragment-secret"
    )

    assert "oauth-code" not in encoded
    assert "oauth-state" not in encoded
    assert "oauth-key" not in encoded
    assert "oauth-nonce" not in encoded
    assert "fragment-secret" not in encoded
    assert "mode=safe" in str(payload["message"])
    assert "#" not in str(payload["message"])


def test_json_formatter_preserves_generic_state_code_and_key_extra_fields() -> None:
    encoded, payload = _format_record(
        "diagnostic state",
        extra={"state": "ready", "code": "E_OK", "key": "research"},
    )

    assert "ready" in encoded
    assert "E_OK" in encoded
    assert "research" in encoded
    assert payload["state"] == "ready"
    assert payload["code"] == "E_OK"
    assert payload["key"] == "research"


def test_json_formatter_redacts_basic_auth_cookie_and_json_secret_text() -> None:
    encoded, payload = _format_record(
        "Authorization: Basic dXNlcjpwYXNz\n"
        "Cookie: session=cookie-secret; theme=dark\n"
        'payload={"password":"hunter2","safe":"ok"}'
    )

    assert "dXNlcjpwYXNz" not in encoded
    assert "cookie-secret" not in encoded
    assert "hunter2" not in encoded
    message = str(payload["message"])
    assert "Authorization: Basic [REDACTED]" in message
    assert "Cookie: [REDACTED]" in message
    assert '"password":"[REDACTED]"' in message
    assert '"safe":"ok"' in message


def test_json_formatter_recursively_redacts_sensitive_extra_fields() -> None:
    encoded, payload = _format_record(
        "request metadata",
        extra={
            "headers": {
                "Authorization": "Bearer header-secret",
                "X-Trace": "trace-ok",
            },
            "nested": [{"refresh_token": "refresh-secret", "count": 3}],
            "token_count": 12,
        },
    )

    assert "header-secret" not in encoded
    assert "refresh-secret" not in encoded
    assert "trace-ok" in encoded
    assert payload["token_count"] == 12
    assert payload["headers"] == {
        "Authorization": "[REDACTED]",
        "X-Trace": "trace-ok",
    }


def test_json_formatter_redacts_semantic_payload_extras_recursively() -> None:
    encoded, payload = _format_record(
        "semantic payload",
        extra={
            "prompt": "private prompt words",
            "nested": {
                "knowledge_body": "private knowledge body",
                "source_chunk": "private source chunk",
                "model_output": "private model output",
                "count": 4,
            },
        },
    )

    assert "private prompt words" not in encoded
    assert "private knowledge body" not in encoded
    assert "private source chunk" not in encoded
    assert "private model output" not in encoded
    assert payload["prompt"] == "[REDACTED_CONTENT]"
    assert payload["nested"] == {
        "knowledge_body": "[REDACTED_CONTENT]",
        "source_chunk": "[REDACTED_CONTENT]",
        "model_output": "[REDACTED_CONTENT]",
        "count": 4,
    }


def test_json_formatter_redacts_semantic_payload_text_and_preserves_safe_context() -> None:
    encoded, payload = _format_record(
        'payload={"model_output":"private answer","duration_ms":12}\n'
        "prompt=private prompt with spaces\n"
        "status=ok"
    )

    assert "private answer" not in encoded
    assert "private prompt with spaces" not in encoded
    message = str(payload["message"])
    assert '"model_output":"[REDACTED_CONTENT]"' in message
    assert '"duration_ms":12' in message
    assert "prompt=[REDACTED_CONTENT]" in message
    assert "status=ok" in message


def test_json_formatter_redacts_semantic_url_query_and_keeps_safe_query() -> None:
    encoded, payload = _format_record(
        "GET https://example.test/search?prompt=private-query&mode=fast"
    )

    assert "private-query" not in encoded
    message = str(payload["message"])
    assert "prompt=%5BREDACTED_CONTENT%5D" in message
    assert "mode=fast" in message


def test_json_formatter_never_stringifies_unknown_extra_objects() -> None:
    class OpaqueSecret:
        def __str__(self) -> str:
            return "opaque-secret-value"

    encoded, payload = _format_record("opaque extra", extra={"opaque": OpaqueSecret()})

    assert "opaque-secret-value" not in encoded
    assert payload["opaque"] == "<type:OpaqueSecret>"


def test_json_formatter_sanitizes_format_args_before_interpolation() -> None:
    class OpaqueSecret:
        stringified = False

        def __str__(self) -> str:
            self.stringified = True
            return "format-arg-secret"

    opaque = OpaqueSecret()
    encoded, payload = _format_record("opaque=%s", args=(opaque,))

    assert opaque.stringified is False
    assert "format-arg-secret" not in encoded
    assert payload["message"] == "opaque=<type:OpaqueSecret>"


def test_json_formatter_sanitizes_authorization_after_safe_interpolation() -> None:
    encoded, payload = _format_record(
        "Authorization: %s",
        args=("Basic dXNlcjpwYXNz",),
    )

    assert "dXNlcjpwYXNz" not in encoded
    assert "formatting-error" not in encoded
    assert payload["message"] == "Authorization: Basic [REDACTED]"


def test_json_formatter_exception_payload_omits_exception_message_and_paths() -> None:
    try:
        raise RuntimeError("password=hunter2")
    except RuntimeError:
        current_exc = sys.exc_info()

    encoded, payload = _format_record("operation failed", exc_info=current_exc)

    assert "hunter2" not in encoded
    exception = payload["exception"]
    assert isinstance(exception, dict)
    assert exception["type"] == "RuntimeError"
    frames = exception["frames"]
    assert isinstance(frames, list)
    assert frames
    for frame in frames:
        assert isinstance(frame, dict)
        assert "/" not in str(frame["file"])
        assert "\\" not in str(frame["file"])


def test_json_formatter_handles_cycles_without_leaking_or_recursing_forever() -> None:
    cyclic: dict[str, object] = {"trace": "safe"}
    cyclic["self"] = cyclic

    encoded, payload = _format_record("cycle", extra={"context": cyclic})

    assert "<cycle>" in encoded
    assert payload["context"] == {"trace": "safe", "self": "<cycle>"}
