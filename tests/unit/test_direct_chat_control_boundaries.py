from __future__ import annotations

import uuid

import pytest

from athena.chat.direct import DirectChatService, _resolve_context_limit
from athena.model.domain import ModelInfo
from athena.retrieval.context import ContextBuilderError


class _Unreachable:
    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"collaborator reached during control validation: {name}")


def _service() -> DirectChatService:
    unreachable = _Unreachable()
    return DirectChatService(
        chat_generation=unreachable,  # type: ignore[arg-type]
        context_packages=unreachable,  # type: ignore[arg-type]
        model_runs=unreachable,  # type: ignore[arg-type]
    )


def _send(**overrides: object) -> None:
    arguments: dict[str, object] = {
        "chat_id": uuid.uuid4(),
        "content": "hello",
    }
    arguments.update(overrides)
    _service().send_message(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_recent_conversation_turns", True),
        ("max_recent_conversation_turns", 1.5),
        ("max_recent_conversation_turns", 0),
        ("max_recent_conversation_turns", 101),
        ("output_reserve", True),
        ("output_reserve", 1.5),
        ("output_reserve", 0),
        ("safety_margin", True),
        ("safety_margin", 1.5),
        ("safety_margin", -1),
        ("temperature", True),
        ("temperature", "0.5"),
        ("temperature", float("nan")),
        ("temperature", float("inf")),
        ("temperature", -0.1),
        ("temperature", 2.1),
    ],
)
def test_invalid_direct_controls_fail_before_any_collaborator(
    field: str,
    value: object,
) -> None:
    with pytest.raises(ContextBuilderError):
        _send(**{field: value})


def test_effective_context_limit_rejects_bool_and_non_integer() -> None:
    model = ModelInfo(
        provider="lm_studio",
        backend_model_id="primary",
        display_name="Primary",
        model_type="llm",
        context_capacity=8192,
        quantization=None,
        loaded=True,
        vision=None,
        trained_for_tool_use=None,
        loaded_context_length=4096,
    )

    for value in (True, False, 1.5, "4096"):
        with pytest.raises(ContextBuilderError):
            _resolve_context_limit(
                model=model,
                requested_limit=value,  # type: ignore[arg-type]
            )
