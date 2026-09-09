from __future__ import annotations

import json

import pytest

from athena.observability.structured_log import (
    REDACTED_CONTENT,
    REDACTED_SECRET,
    LogEvent,
    LogLevel,
    redact_value,
    sanitize_url,
    serialize_event,
)


def _event(**overrides: object) -> LogEvent:
    values: dict[str, object] = {
        "timestamp": "2026-09-09T14:50:00Z",
        "level": LogLevel.INFO,
        "component": "tests",
        "event": "unit.complete",
        "request_id": "req-1",
    }
    values.update(overrides)
    return LogEvent(**values)  # type: ignore[arg-type]


def test_log_event_schema_is_stable_and_keeps_optional_correlation_fields() -> None:
    payload = _event(
        job_id="job-1",
        processing_run_id="run-1",
        error_code="E_TEST",
        duration_ms=12,
        attributes={"count": 3},
    ).to_dict()

    assert list(payload) == [
        "timestamp",
        "level",
        "component",
        "event",
        "request_id",
        "job_id",
        "processing_run_id",
        "error_code",
        "duration_ms",
        "attributes",
    ]
    assert payload["level"] == "INFO"
    assert payload["job_id"] == "job-1"
    assert payload["processing_run_id"] == "run-1"
    assert payload["duration_ms"] == 12


def test_serialize_event_emits_exactly_one_json_line() -> None:
    encoded = serialize_event(_event(attributes={"unicode": "✓"}))

    assert encoded.endswith("\n")
    assert encoded.count("\n") == 1
    decoded = json.loads(encoded)
    assert decoded["event"] == "unit.complete"
    assert decoded["attributes"]["unicode"] == "✓"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("Authorization", "Bearer top-secret"),
        ("proxy-authorization", "Basic top-secret"),
        ("Cookie", "session=top-secret"),
        ("X-API-Key", "top-secret"),
        ("api_key", "top-secret"),
        ("password", "top-secret"),
        ("client_secret", "top-secret"),
        ("access_token", "top-secret"),
    ],
)
def test_known_secret_fields_are_redacted_recursively(
    field_name: str,
    value: str,
) -> None:
    payload = redact_value({"outer": {field_name: value}})

    assert payload == {"outer": {field_name: REDACTED_SECRET}}
    assert "top-secret" not in json.dumps(payload)


@pytest.mark.parametrize(
    "field_name",
    [
        "prompt",
        "content",
        "knowledge_body",
        "source_chunk",
        "model_output",
        "title",
    ],
)
def test_semantic_payload_fields_are_not_copied_into_technical_logs(
    field_name: str,
) -> None:
    payload = redact_value({field_name: "private phrase"})

    assert payload == {field_name: REDACTED_CONTENT}
    assert "private phrase" not in json.dumps(payload)


def test_sensitive_url_query_parameters_are_redacted_without_dropping_safe_context() -> None:
    sanitized = sanitize_url(
        "https://example.test/search?q=safe&api_key=secret&access_token=token#part"
    )

    assert sanitized == (
        "https://example.test/search?"
        "q=safe&api_key=%5BREDACTED%5D&access_token=%5BREDACTED%5D#part"
    )
    assert "secret" not in sanitized
    assert "token=token" not in sanitized


def test_nested_http_url_is_sanitized_even_without_url_field_name() -> None:
    payload = redact_value(
        {"dependency": ["https://example.test/a?password=hidden&mode=fast"]}
    )

    assert payload == {
        "dependency": [
            "https://example.test/a?password=%5BREDACTED%5D&mode=fast"
        ]
    }


def test_exception_message_and_repr_are_never_serialized() -> None:
    error = RuntimeError("Bearer secret-value")

    payload = redact_value({"exception": error})

    assert payload == {"exception": {"exception_class": "RuntimeError"}}
    assert "secret-value" not in json.dumps(payload)


def test_unsupported_objects_fail_closed_instead_of_using_repr() -> None:
    class SensitiveObject:
        def __repr__(self) -> str:
            return "SensitiveObject(secret-value)"

    with pytest.raises(TypeError, match="explicit safe conversion"):
        redact_value({"value": SensitiveObject()})


@pytest.mark.parametrize("duration_ms", [-1, True, 1.5])
def test_duration_must_be_non_negative_integer(duration_ms: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _event(duration_ms=duration_ms)


def test_non_finite_numbers_are_rejected() -> None:
    with pytest.raises(ValueError, match="finite JSON"):
        serialize_event(_event(attributes={"ratio": float("nan")}))
