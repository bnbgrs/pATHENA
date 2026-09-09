from __future__ import annotations

import pytest

from athena.chat.direct import _direct_context_configuration, _effective_output_reserve
from athena.retrieval.context import ContextBuilderError


def test_output_reserve_adapts_to_2048_loaded_context() -> None:
    assert _effective_output_reserve(
        context_limit=2048,
        estimated_input_tokens=64,
        requested_output_reserve=2048,
        safety_margin=256,
    ) == 1728


def test_output_reserve_keeps_configured_reserve_when_context_allows_it() -> None:
    assert _effective_output_reserve(
        context_limit=8192,
        estimated_input_tokens=512,
        requested_output_reserve=2048,
        safety_margin=256,
    ) == 2048


def test_output_reserve_does_not_inflate_smaller_requested_limit() -> None:
    assert _effective_output_reserve(
        context_limit=2048,
        estimated_input_tokens=64,
        requested_output_reserve=128,
        safety_margin=256,
    ) == 128


def test_output_reserve_preserves_safety_margin_at_one_token_boundary() -> None:
    assert _effective_output_reserve(
        context_limit=2048,
        estimated_input_tokens=1791,
        requested_output_reserve=2048,
        safety_margin=256,
    ) == 1


def test_output_reserve_preserves_one_token_with_zero_safety_margin() -> None:
    assert _effective_output_reserve(
        context_limit=2048,
        estimated_input_tokens=2047,
        requested_output_reserve=2048,
        safety_margin=0,
    ) == 1


def test_output_reserve_fails_closed_when_input_and_margin_exhaust_context() -> None:
    with pytest.raises(ContextBuilderError, match="exhaust the active model context"):
        _effective_output_reserve(
            context_limit=2048,
            estimated_input_tokens=1792,
            requested_output_reserve=2048,
            safety_margin=256,
        )


def test_direct_chat_configuration_records_requested_and_effective_reserve() -> None:
    configuration = _direct_context_configuration(
        context_limit=2048,
        max_recent_conversation_turns=8,
        requested_output_reserve=2048,
        effective_output_reserve=1728,
        safety_margin=256,
    )

    assert configuration["requested_output_reserve"] == 2048
    assert configuration["effective_output_reserve"] == 1728
    assert configuration["effective_context_limit"] == 2048
    assert configuration["safety_margin"] == 256
