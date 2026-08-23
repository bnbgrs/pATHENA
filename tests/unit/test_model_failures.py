from __future__ import annotations

import pytest

from athena.model.failures import (
    ProviderFailure,
    ProviderFailureKind,
    ProviderFailureRetryClass,
)


@pytest.mark.parametrize(
    "kind,retry_class",
    [
        (ProviderFailureKind.TIMEOUT, ProviderFailureRetryClass.RETRYABLE),
        (ProviderFailureKind.RESOURCE_EXHAUSTED, ProviderFailureRetryClass.RETRYABLE),
        (ProviderFailureKind.UNAVAILABLE, ProviderFailureRetryClass.RETRYABLE),
        (ProviderFailureKind.BACKEND_CRASH, ProviderFailureRetryClass.RETRYABLE),
        (ProviderFailureKind.INVALID_RESPONSE, ProviderFailureRetryClass.TERMINAL),
        (ProviderFailureKind.REFUSAL, ProviderFailureRetryClass.TERMINAL),
        (
            ProviderFailureKind.CONTEXT_LIMIT,
            ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED,
        ),
        (
            ProviderFailureKind.OUTPUT_LIMIT,
            ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED,
        ),
        (ProviderFailureKind.UNKNOWN, ProviderFailureRetryClass.UNKNOWN),
    ],
)
def test_provider_failure_has_stable_retry_class(
    kind: ProviderFailureKind,
    retry_class: ProviderFailureRetryClass,
) -> None:
    failure = ProviderFailure(kind=kind, code="backend_error")

    assert failure.retry_class is retry_class
    assert failure.retryable is (retry_class is ProviderFailureRetryClass.RETRYABLE)
    assert failure.terminal is (retry_class is ProviderFailureRetryClass.TERMINAL)
    assert failure.request_change_required is (
        retry_class is ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED
    )


def test_provider_failure_exposes_sanitized_durable_code() -> None:
    failure = ProviderFailure(
        kind=ProviderFailureKind.TIMEOUT,
        code="generation_timeout",
    )

    assert failure.durable_code() == "provider.timeout.generation_timeout"


@pytest.mark.parametrize(
    "code",
    [
        "",
        " ",
        " leading",
        "trailing ",
        "contains space",
        "contains/slash",
        "contains:colon",
        "x" * 129,
    ],
)
def test_provider_failure_rejects_unsafe_durable_code(code: str) -> None:
    with pytest.raises(ValueError):
        ProviderFailure(
            kind=ProviderFailureKind.UNAVAILABLE,
            code=code,
        )


def test_provider_failure_rejects_non_text_code() -> None:
    with pytest.raises(TypeError, match="must be text"):
        ProviderFailure(
            kind=ProviderFailureKind.UNAVAILABLE,
            code=123,  # type: ignore[arg-type]
        )


def test_provider_failure_rejects_non_enum_kind() -> None:
    with pytest.raises(TypeError, match="ProviderFailureKind"):
        ProviderFailure(
            kind="timeout",  # type: ignore[arg-type]
            code="generation_timeout",
        )
