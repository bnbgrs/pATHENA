from __future__ import annotations

import os
from pathlib import Path
from typing import cast

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from athena.api.contracts import HealthResponse, ModelResponse, ProviderHealthResponse
from athena.desktop.api_controller import (
    DesktopApiController,
    DesktopApiSnapshot,
    SnapshotFreshness,
)
from athena.desktop.pathena_secondary_navigation import (
    install_settings_secondary_navigation,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _model(
    backend_model_id: str,
    display_name: str,
    *,
    loaded: bool,
    context_capacity: int,
    loaded_context_length: int | None,
) -> ModelResponse:
    return ModelResponse(
        provider="lm_studio",
        backend_model_id=backend_model_id,
        display_name=display_name,
        model_type="llm",
        context_capacity=context_capacity,
        quantization="Q4",
        loaded=loaded,
        vision=False,
        trained_for_tool_use=True,
        loaded_context_length=loaded_context_length,
    )


def _models() -> tuple[ModelResponse, ...]:
    return (
        _model(
            "qwen-loaded",
            "Qwen Loaded",
            loaded=True,
            context_capacity=128_000,
            loaded_context_length=48_000,
        ),
        _model(
            "llama-available",
            "Llama Available",
            loaded=False,
            context_capacity=65_536,
            loaded_context_length=None,
        ),
    )


def _snapshot(
    models: tuple[ModelResponse, ...],
    *,
    provider_status: str = "ready",
    model_error: str | None = None,
    model_freshness: SnapshotFreshness | None = None,
) -> DesktopApiSnapshot:
    return DesktopApiSnapshot(
        health=HealthResponse(
            api_version="v1",
            core_status="ok",
            detail=None,
        ),
        provider=ProviderHealthResponse(
            provider="lm_studio",
            status=provider_status,
            detail=None,
        ),
        models=models,
        chats=(),
        model_error=model_error,
        model_freshness=model_freshness,
    )


class _ChatRecorder:
    def __init__(self) -> None:
        self.last_send: dict[str, object] | None = None

    def send_message(self, **kwargs: object) -> None:
        self.last_send = kwargs


def test_issue_244_model_selectors_use_real_snapshot_and_stay_synchronized() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        secondary = install_settings_secondary_navigation(window)
        window.apply_api_snapshot(_snapshot(_models()))

        expected_ids = ["qwen-loaded", "llama-available"]
        assert [
            window.model_selector.itemData(index)
            for index in range(window.model_selector.count())
        ] == expected_ids
        assert [
            window.settings_model_selector.itemData(index)
            for index in range(window.settings_model_selector.count())
        ] == expected_ids
        assert "Loaded" in window.model_selector.itemText(0)
        assert "Available" in window.model_selector.itemText(1)
        assert secondary.sections[0].target is window.settings_model_selector

        settings_index = window.settings_model_selector.findData("llama-available")
        assert settings_index >= 0
        window.settings_model_selector.setCurrentIndex(settings_index)
        window._on_settings_model_selected(settings_index)

        assert window._selected_model_id() == "llama-available"
        assert window.model_selector.currentData() == "llama-available"
        assert window.settings_model_selector.currentData() == "llama-available"
        assert window.context_spin.maximum() == 65_536

        chat_index = window.model_selector.findData("qwen-loaded")
        assert chat_index >= 0
        window.model_selector.setCurrentIndex(chat_index)
        window._on_model_selected(chat_index)

        assert window._selected_model_id() == "qwen-loaded"
        assert window.settings_model_selector.currentData() == "qwen-loaded"
        assert window.context_spin.maximum() == 48_000

        recorder = _ChatRecorder()
        window.api_controller = cast(DesktopApiController, recorder)
        window.prompt_input.setText("Use the selected model")
        window._submit_prompt()

        assert recorder.last_send is not None
        assert recorder.last_send["model_id"] == "qwen-loaded"
        assert recorder.last_send["effective_context_limit"] == 48_000
    finally:
        window.close()


def test_issue_244_empty_and_unavailable_model_states_remain_explicit() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        install_settings_secondary_navigation(window)

        window.apply_api_snapshot(
            _snapshot(
                (),
                provider_status="unavailable",
                model_error="LM Studio is unavailable.",
                model_freshness="unavailable",
            )
        )
        for selector in (
            window.model_selector,
            window.settings_model_selector,
        ):
            assert selector.count() == 1
            assert selector.itemData(0) is None
            assert "unavailable" in selector.itemText(0).casefold()
            assert not selector.isEnabled()

        window.apply_api_snapshot(_snapshot(()))
        for selector in (
            window.model_selector,
            window.settings_model_selector,
        ):
            assert selector.count() == 1
            assert selector.itemData(0) is None
            assert "no local llm models" in selector.itemText(0).casefold()
            assert not selector.isEnabled()
    finally:
        window.close()


@pytest.mark.parametrize("width,height", [(1180, 720), (1660, 980)])
def test_issue_244_model_chooser_renders_in_chat_and_settings_at_release_sizes(
    tmp_path: Path,
    width: int,
    height: int,
) -> None:
    app = _app()
    window = PathenaMainWindow()
    try:
        secondary = install_settings_secondary_navigation(window)
        window.apply_api_snapshot(_snapshot(_models()))
        window.resize(width, height)
        window.show()
        app.processEvents()

        window.navigation.setCurrentRow(0)
        app.processEvents()
        assert window.model_selector.isVisible()
        assert not window.model_selector.visibleRegion().isEmpty()
        assert window.model_selector.currentData() == "qwen-loaded"
        chat_capture = window.grab()
        assert not chat_capture.isNull()
        assert chat_capture.save(
            str(tmp_path / f"issue-244-chat-{width}x{height}.png"),
            "PNG",
        )

        window.navigation.setCurrentRow(6)
        app.processEvents()
        assert secondary.sections[0].target is window.settings_model_selector
        assert window.settings_model_selector.isVisible()
        assert not window.settings_model_selector.visibleRegion().isEmpty()
        assert window.settings_model_selector.currentData() == "qwen-loaded"
        settings_capture = window.grab()
        assert not settings_capture.isNull()
        assert settings_capture.save(
            str(tmp_path / f"issue-244-settings-{width}x{height}.png"),
            "PNG",
        )
    finally:
        window.close()
