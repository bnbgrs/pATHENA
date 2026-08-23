from __future__ import annotations

from athena.storage.schema_error_sanitization import (
    _MAX_PERSISTED_ERROR_CODE_LENGTH,
    _sanitize_checkpoint_error_payload,
    _sanitize_persisted_error_value,
)


def test_error_code_at_total_length_boundary_is_preserved() -> None:
    value = "E" * _MAX_PERSISTED_ERROR_CODE_LENGTH

    # One segment is independently capped at 128, so construct two segments.
    value = "E" * 128 + ":" + "S" * 127
    assert len(value) == _MAX_PERSISTED_ERROR_CODE_LENGTH

    assert _sanitize_persisted_error_value(value) == value


def test_overlong_segmented_error_code_is_reduced_to_safe_prefix() -> None:
    value = "ProviderError:" + ":".join("E" for _ in range(300))

    assert len(value) > _MAX_PERSISTED_ERROR_CODE_LENGTH
    assert _sanitize_persisted_error_value(value) == "ProviderError"


def test_overlong_unstructured_error_becomes_generic_code() -> None:
    value = "X" * (_MAX_PERSISTED_ERROR_CODE_LENGTH + 1)

    assert _sanitize_persisted_error_value(value) == "OperationalError"


def test_checkpoint_sanitization_applies_total_length_bound() -> None:
    value = {
        "reason": "provider",
        "detail": "ProviderError:" + ":".join("E" for _ in range(300)),
    }

    sanitized, changed = _sanitize_checkpoint_error_payload(
        job_type="source.analyze",
        value=value,
    )

    assert changed is True
    assert sanitized == {"reason": "provider", "detail": "ProviderError"}
