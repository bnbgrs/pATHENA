from __future__ import annotations

from collections.abc import Iterator, Sequence

import pytest

from athena.hardware_acceptance import (
    INFERENCE_MARKER,
    HardwareAcceptanceError,
    _run_live_inference,
    _video_controller_names_from_payload,
)
from athena.model.domain import ModelChatMessage, ModelInfo


def _model() -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id="local-model",
        display_name="local-model",
        model_type="llm",
        context_capacity=8192,
        quantization="test",
        loaded=True,
        vision=None,
        trained_for_tool_use=None,
    )


class _Provider:
    base_url = "http://127.0.0.1:1234"

    def __init__(self, response: str) -> None:
        self.response = response

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (_model(),)

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        del model_id, messages, max_output_tokens, reasoning_mode, temperature
        yield self.response


def test_video_controller_payload_rejects_mixed_type_names() -> None:
    with pytest.raises(HardwareAcceptanceError, match="invalid controller name"):
        _video_controller_names_from_payload(
            '{"names":["AMD Radeon RX 7900 XTX",123]}'
        )


def test_video_controller_payload_rejects_blank_names() -> None:
    with pytest.raises(HardwareAcceptanceError, match="invalid controller name"):
        _video_controller_names_from_payload(
            '{"names":["AMD Radeon RX 7900 XTX",""]}'
        )


def test_live_inference_rejects_marker_embedded_in_extra_text() -> None:
    provider = _Provider(f"prefix {INFERENCE_MARKER} suffix")

    with pytest.raises(HardwareAcceptanceError, match="exactly the acceptance marker"):
        _run_live_inference(provider, _model())


def test_live_inference_accepts_only_incidental_surrounding_whitespace() -> None:
    provider = _Provider(f"  {INFERENCE_MARKER}\r\n")

    assert _run_live_inference(provider, _model()) == INFERENCE_MARKER
