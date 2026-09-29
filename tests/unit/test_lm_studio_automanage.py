from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from typing import Any

import pytest

from athena.chat.generation import ChatGenerationService
from athena.model.adapters import lm_studio
from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.domain import ModelInfo


class _Response:
    def __init__(self, payload: Mapping[str, Any]) -> None:
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> bool:
        del args
        return False

    def read(self) -> bytes:
        return self._raw


def _model_payload(*, loaded: bool) -> dict[str, Any]:
    return {
        "key": "example/qwen-q4",
        "display_name": "Qwen Example",
        "type": "llm",
        "max_context_length": 32768,
        "quantization": {"name": "Q4_K_M"},
        "capabilities": {
            "vision": False,
            "trained_for_tool_use": True,
        },
        "loaded_instances": (
            [
                {
                    "id": "example/qwen-q4:runtime",
                    "config": {"context_length": 8192},
                }
            ]
            if loaded
            else []
        ),
    }


def test_runtime_start_uses_headless_server_without_gui(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = LMStudioProvider("http://127.0.0.1:1234")
    calls: list[tuple[str, tuple[str, ...], float]] = []

    monkeypatch.setattr(
        LMStudioProvider,
        "_find_lms_cli",
        staticmethod(lambda: r"C:\Users\test\.lmstudio\bin\lms.exe"),
    )

    def fake_run(
        cli: str,
        args: tuple[str, ...],
        *,
        timeout_seconds: float,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((cli, tuple(args), timeout_seconds))
        return subprocess.CompletedProcess([cli, *args], 0, "", "")

    monkeypatch.setattr(
        LMStudioProvider,
        "_run_lms",
        staticmethod(fake_run),
    )

    assert provider._try_start_local_runtime() is True
    assert calls == [
        (
            r"C:\Users\test\.lmstudio\bin\lms.exe",
            ("daemon", "up", "--json"),
            15.0,
        ),
        (
            r"C:\Users\test\.lmstudio\bin\lms.exe",
            (
                "server",
                "start",
                "--port",
                "1234",
                "--bind",
                "127.0.0.1",
            ),
            30.0,
        ),
    ]


def test_provider_loads_downloaded_model_through_native_v1_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = LMStudioProvider(
        "http://127.0.0.1:1234",
        timeout_seconds=1.0,
        generation_timeout_seconds=2.0,
    )
    loaded = False
    calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def fake_open(request: Any, timeout: float) -> _Response:
        nonlocal loaded
        del timeout
        body = (
            None
            if request.data is None
            else json.loads(request.data.decode("utf-8"))
        )
        calls.append((request.get_method(), request.full_url, body))

        if request.full_url == provider.models_url:
            return _Response({"models": [_model_payload(loaded=loaded)]})
        if request.full_url == provider.model_load_url:
            assert body == {
                "model": "example/qwen-q4",
                "context_length": 8192,
            }
            loaded = True
            return _Response(
                {
                    "type": "llm",
                    "instance_id": "example/qwen-q4:runtime",
                    "load_time_seconds": 0.1,
                    "status": "loaded",
                }
            )
        raise AssertionError(request.full_url)

    monkeypatch.setattr(lm_studio, "open_local_request", fake_open)

    model = provider.load_model(
        "example/qwen-q4",
        context_length=8192,
    )

    assert model.loaded is True
    assert model.backend_model_id == "example/qwen-q4"
    assert any(url == provider.model_load_url for _method, url, _body in calls)


class _ManagedProvider:
    provider_id = "lm_studio"

    def __init__(self) -> None:
        self.load_calls: list[tuple[str, int | None]] = []

    def health(self):  # pragma: no cover - not needed by this unit
        raise AssertionError

    def discover_models(self) -> tuple[ModelInfo, ...]:
        loaded = bool(self.load_calls)
        return (
            ModelInfo(
                provider="lm_studio",
                backend_model_id="example/qwen-q4",
                display_name="Qwen Example",
                model_type="llm",
                context_capacity=32768,
                quantization="Q4_K_M",
                loaded=loaded,
                vision=False,
                trained_for_tool_use=True,
                loaded_context_length=8192 if loaded else None,
            ),
        )

    def load_model(
        self,
        model_id: str,
        *,
        context_length: int | None = None,
    ) -> ModelInfo:
        self.load_calls.append((model_id, context_length))
        return self.discover_models()[0]


def test_selected_unloaded_model_is_auto_loaded_and_returned() -> None:
    provider = _ManagedProvider()
    service = ChatGenerationService(
        chat=None,  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
    )

    model = service.select_model(
        "example/qwen-q4",
        context_length=8192,
    )

    assert provider.load_calls == [("example/qwen-q4", 8192)]
    assert model.loaded is True
    assert model.backend_model_id == "example/qwen-q4"


def test_explicit_context_change_reloads_same_model_instead_of_duplication(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = LMStudioProvider(
        "http://127.0.0.1:1234",
        timeout_seconds=1.0,
        generation_timeout_seconds=2.0,
    )
    state = {"loaded": True, "context": 8192}
    calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def payload() -> dict[str, Any]:
        raw = _model_payload(loaded=state["loaded"])
        if state["loaded"]:
            raw["loaded_instances"][0]["config"]["context_length"] = state["context"]
        return raw

    def fake_open(request: Any, timeout: float) -> _Response:
        del timeout
        body = (
            None
            if request.data is None
            else json.loads(request.data.decode("utf-8"))
        )
        calls.append((request.get_method(), request.full_url, body))

        if request.full_url == provider.models_url:
            return _Response({"models": [payload()]})
        if request.full_url == provider.model_unload_url:
            assert body == {"instance_id": "example/qwen-q4:runtime"}
            state["loaded"] = False
            return _Response({"status": "unloaded"})
        if request.full_url == provider.model_load_url:
            assert body == {
                "model": "example/qwen-q4",
                "context_length": 16384,
            }
            state["loaded"] = True
            state["context"] = 16384
            return _Response(
                {
                    "type": "llm",
                    "instance_id": "example/qwen-q4:runtime",
                    "load_time_seconds": 0.1,
                    "status": "loaded",
                }
            )
        raise AssertionError(request.full_url)

    monkeypatch.setattr(lm_studio, "open_local_request", fake_open)

    model = provider.load_model(
        "example/qwen-q4",
        context_length=16384,
    )

    assert model.loaded is True
    assert model.loaded_context_length == 16384
    lifecycle = [
        url
        for method, url, _body in calls
        if method == "POST"
    ]
    assert lifecycle == [
        provider.model_unload_url,
        provider.model_load_url,
    ]
