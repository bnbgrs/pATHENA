from __future__ import annotations

import base64
import json
import uuid
from typing import Any
from unittest.mock import Mock
from urllib.request import Request

import pytest

from athena.api.service import CoreApiFacade
from athena.chat.models import ChatThread
from athena.model.adapters import lm_studio as lm_studio_module
from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.domain import (
    ModelCapabilitySupport,
    ModelChatMessage,
    ModelImageInput,
    ModelInfo,
    ProviderHealth,
    ProviderHealthStatus,
)
from athena.observability.health import HealthService

CHAT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
IMAGE_SOURCE_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


class _StreamResponse:
    def __init__(self, lines: tuple[bytes, ...]) -> None:
        self._lines = lines

    def __enter__(self) -> _StreamResponse:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        del exc_type, exc, traceback

    def __iter__(self):
        return iter(self._lines)


class _Provider:
    @property
    def provider_id(self) -> str:
        return "lm_studio"

    def health(self) -> ProviderHealth:
        return ProviderHealth(status=ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return ()


class _ImageSources:
    def __init__(self, payload: bytes = b"verified-image-bytes") -> None:
        self.payload = payload
        self.reads: list[tuple[uuid.UUID, int]] = []

    def read_image_payload(
        self,
        source_id: uuid.UUID,
        *,
        max_bytes: int,
    ) -> tuple[str, bytes]:
        self.reads.append((source_id, max_bytes))
        return ("image/png", self.payload)


def _facade(
    *,
    image_sources: _ImageSources,
) -> tuple[CoreApiFacade, Mock]:
    health = HealthService()
    health.mark_ok()
    chat = Mock()
    chat.load_chat.return_value = ChatThread(
        chat_id=CHAT_ID,
        started_at_us=1,
        ended_at_us=None,
        archive_mode="standard",
        lifecycle_state="active",
        messages=(),
    )
    direct = Mock()
    facade = CoreApiFacade(
        health=health,
        chat=chat,
        model_provider=_Provider(),
        direct_chat=direct,
        image_sources=image_sources,
    )
    return facade, direct


def test_lm_studio_vision_stream_encodes_images_in_final_user_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, Any] = {}

    def fake_open(
        request: Request,
        *,
        timeout: float,
    ) -> _StreamResponse:
        assert timeout > 0
        assert request.data is not None
        observed["url"] = request.full_url
        observed["payload"] = json.loads(request.data.decode("utf-8"))
        return _StreamResponse(
            (
                b'data: {"choices":[{"delta":{"content":"seen"},'
                b'"finish_reason":null}]}\n',
                b"data: [DONE]\n",
            )
        )

    monkeypatch.setattr(
        lm_studio_module,
        "open_local_request",
        fake_open,
    )
    provider = LMStudioProvider(base_url="http://127.0.0.1:1234")
    image = ModelImageInput(
        media_type="image/png",
        data=b"\x89PNG\r\n\x1a\nvision",
    )

    chunks = list(
        provider.stream_chat_vision(
            model_id="local/vision-model",
            messages=(
                ModelChatMessage(role="system", content="be precise"),
                ModelChatMessage(role="user", content="describe this image"),
            ),
            images=(image,),
            max_output_tokens=256,
            reasoning_mode="off",
            temperature=0.2,
        )
    )

    assert chunks == ["seen"]
    assert observed["url"] == "http://127.0.0.1:1234/v1/chat/completions"
    payload = observed["payload"]
    assert payload["model"] == "local/vision-model"
    assert payload["stream"] is True
    assert payload["max_tokens"] == 256
    assert payload["reasoning_effort"] == "none"
    assert payload["temperature"] == 0.2
    assert payload["messages"][0] == {
        "role": "system",
        "content": "be precise",
    }
    assert payload["messages"][1] == {
        "role": "user",
        "content": [
            {"type": "text", "text": "describe this image"},
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        "data:image/png;base64,"
                        + base64.b64encode(image.data).decode("ascii")
                    )
                },
            },
        ],
    }


def test_lm_studio_vision_requires_final_user_message() -> None:
    provider = LMStudioProvider(base_url="http://127.0.0.1:1234")

    with pytest.raises(
        ValueError,
        match="final user message",
    ):
        list(
            provider.stream_chat_vision(
                model_id="local/vision-model",
                messages=(
                    ModelChatMessage(role="assistant", content="already answered"),
                ),
                images=(
                    ModelImageInput(
                        media_type="image/png",
                        data=b"image",
                    ),
                ),
            )
        )


def test_lm_studio_model_metadata_preserves_truthful_vision_capability() -> None:
    provider = LMStudioProvider(base_url="http://127.0.0.1:1234")

    supported = provider._parse_model(
        {
            "key": "local/vision-model",
            "display_name": "Vision",
            "type": "llm",
            "loaded_instances": [],
            "capabilities": {
                "vision": True,
                "trained_for_tool_use": False,
            },
        }
    )
    unknown = provider._parse_model(
        {
            "key": "local/unknown-model",
            "display_name": "Unknown",
            "type": "llm",
            "loaded_instances": [],
        }
    )

    assert supported.vision is True
    assert supported.capabilities.vision is ModelCapabilitySupport.SUPPORTED
    assert unknown.vision is None
    assert unknown.capabilities.vision is ModelCapabilitySupport.UNKNOWN


def test_core_resolves_durable_image_source_before_direct_generation() -> None:
    sources = _ImageSources()
    facade, direct = _facade(image_sources=sources)

    thread = facade.send_chat_message(
        str(CHAT_ID),
        content="describe this",
        requested_model_id="local/vision-model",
        image_source_ids=(str(IMAGE_SOURCE_ID),),
    )

    assert thread.chat_id == str(CHAT_ID)
    assert sources.reads == [(IMAGE_SOURCE_ID, 12 * 1024 * 1024)]
    direct.send_message.assert_called_once()
    kwargs = direct.send_message.call_args.kwargs
    assert kwargs["image_source_ids"] == (IMAGE_SOURCE_ID,)
    assert len(kwargs["image_inputs"]) == 1
    image = kwargs["image_inputs"][0]
    assert isinstance(image, ModelImageInput)
    assert image.media_type == "image/png"
    assert image.data == b"verified-image-bytes"


def test_core_rejects_duplicate_image_sources_before_archive_read() -> None:
    sources = _ImageSources()
    facade, direct = _facade(image_sources=sources)

    with pytest.raises(ValueError, match="unique"):
        facade.send_chat_message(
            str(CHAT_ID),
            content="describe this",
            requested_model_id="local/vision-model",
            image_source_ids=(
                str(IMAGE_SOURCE_ID),
                str(IMAGE_SOURCE_ID),
            ),
        )

    assert sources.reads == []
    direct.send_message.assert_not_called()
