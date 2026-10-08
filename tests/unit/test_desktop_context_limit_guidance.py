"""Focused, headless tests for truthful context-overflow UI guidance."""

from athena.desktop.context_limit_guidance import context_limit_guidance


def test_direct_context_overflow_explained_without_fabricated_usage() -> None:
    text = context_limit_guidance(
        "send", "Current user input and safety margin exhaust the active model context."
    )
    assert text is not None
    assert "reopen this chat" in text
    assert "unavailable" in text
    assert "32,768" not in text


def test_grounded_provider_overflow_explained() -> None:
    assert context_limit_guidance("send_grounded", "maximum context length exceeded")


def test_regenerate_overflow_explained() -> None:
    assert context_limit_guidance("regenerate", "prompt too long")


def test_unrelated_provider_error_not_misdiagnosed() -> None:
    assert context_limit_guidance("send", "LM Studio provider timed out") is None
    assert context_limit_guidance("send", "Tokenizer unavailable") is None


def test_unrelated_operation_not_relabelled() -> None:
    assert context_limit_guidance("delete", "context length exceeded") is None
