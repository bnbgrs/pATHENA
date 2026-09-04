from __future__ import annotations

import os
from typing import cast
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from athena.api.contracts import HealthResponse, ModelResponse, ProviderHealthResponse
from athena.desktop.api_controller import DesktopApiSnapshot
from athena.desktop.app import create_application
from athena.desktop.pathena_settings_runtime import install_settings_runtime
from athena.desktop.pathena_window import PathenaMainWindow


def _snapshot_with_selected_model() -> DesktopApiSnapshot:
    return DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="LM Studio",
            status="ready",
            detail=None,
        ),
        models=(
            ModelResponse(
                provider="LM Studio",
                backend_model_id="qwen-local-backend-id",
                display_name="Local Qwen",
                model_type="llm",
                context_capacity=65_536,
                quantization="Q4",
                loaded=True,
                vision=False,
                trained_for_tool_use=True,
                loaded_context_length=65_536,
            ),
        ),
        chats=(),
        model_error=None,
        model_freshness=None,
    )


def test_persistence_state_fails_closed_when_no_model_is_selected(tmp_path) -> None:
    app: QApplication = create_application(["pathena-settings-no-model-test"])
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    try:
        window.model_selector.clear()
        runtime.hydrate_selected_model()

        assert runtime.persistence_value.text() == "Per-model settings · choose a model"
        assert runtime.persistence_value.property("pathenaUiState") == "idle"
        assert runtime.persistence_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.persistence_value.accessibleDescription() == runtime.persistence_value.text()
    finally:
        window.close()
        app.processEvents()


def test_persistence_state_fails_closed_for_unsaved_selected_model(tmp_path) -> None:
    app: QApplication = create_application(["pathena-settings-unsaved-model-test"])
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    snapshot = _snapshot_with_selected_model()
    try:
        window.apply_api_snapshot(snapshot)
        runtime.hydrate_selected_model()

        assert runtime.persistence_value.text() == "Local Qwen · defaults not yet saved"
        assert runtime.persistence_value.property("pathenaUiState") == "idle"
        assert runtime.persistence_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.persistence_value.accessibleDescription() == runtime.persistence_value.text()
    finally:
        window.close()
        app.processEvents()


def test_unreadable_settings_use_display_name_and_fail_closed() -> None:
    app: QApplication = create_application(["pathena-settings-unreadable-model-test"])
    window = PathenaMainWindow(api_controller=None)
    settings = Mock(spec=QSettings)
    settings.value.side_effect = (
        lambda key, default=None: "qwen-local-backend-id" if key == "model_id" else default
    )
    settings.status.return_value = QSettings.Status.AccessError
    runtime = install_settings_runtime(window, None, settings=cast(QSettings, settings))
    snapshot = _snapshot_with_selected_model()
    try:
        window.apply_api_snapshot(snapshot)
        runtime.hydrate_selected_model()

        assert runtime.persistence_value.text() == "Local Qwen · local settings unreadable"
        assert "qwen-local-backend-id" not in runtime.persistence_value.text()
        assert runtime.persistence_value.property("pathenaUiState") == "error"
        assert runtime.persistence_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.persistence_value.accessibleDescription() == runtime.persistence_value.text()
    finally:
        window.close()
        app.processEvents()
