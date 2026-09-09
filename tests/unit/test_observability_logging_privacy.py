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
        "&mode=safe#access_token=fragment-secret"
    )

    assert "oauth-code" not in encoded
    assert "oauth-state" not in encoded
    assert "fragment-secret" not in encoded
    assert "mode=safe" in str(payload["message"])
    assert "#" not in str(payload["message"])


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
