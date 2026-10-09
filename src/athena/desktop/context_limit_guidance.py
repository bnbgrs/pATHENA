"""User-facing guidance for confirmed context-window failures.

This is presentation-only: it does not infer token counts or retry a request.
"""

from __future__ import annotations

_CONTEXT_LIMIT_MARKERS = (
    "context length exceeded",
    "maximum context length",
    "context window exceeded",
    "context window is full",
    "context budget exceeded",
    "context limit exceeded",
    "context overflow",
    "context_length_exceeded",
    "exhaust the active model context",
    "exhausts the active model context",
    "exceeds the active model context",
    "prompt too long",
    "token limit exceeded",
    "token budget exhausted",
    "input exceeds context",
    "does not fit the context",
)


def context_limit_guidance(operation: str, message: str) -> str | None:
    """Explain a known context overflow without inventing usage measurements."""
    if operation not in {"send", "send_grounded", "regenerate"}:
        return None
    normalized = " ".join(message.casefold().split())
    if not any(marker in normalized for marker in _CONTEXT_LIMIT_MARKERS):
        return None
    return (
        "Context window limit: this request could not fit within the model's "
        "available context budget. The loaded LM Studio model and CTX setting "
        "determine the limit; MAX OUTPUT reserves room for the response. "
        "Try a shorter new prompt, a smaller output reservation, or a model "
        "with a larger supported context. To inspect the original conversation, "
        "reopen this chat and scroll through its saved messages. Viewing those "
        "messages does not mean they were included in this model request. "
        "Exact input-token usage and omitted-message counts are unavailable "
        "until Core exposes the run's ContextPackage/ProcessingRun data."
    )
