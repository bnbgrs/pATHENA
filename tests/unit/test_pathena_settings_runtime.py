from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from athena.api.contracts import (
    HealthResponse,
    ModelResponse,
    ProviderHealthResponse,
)
from athena.desktop.api_controller import (
    DesktopApiController,
    DesktopApiSnapshot,
    SnapshotFreshness,
)
from athena.desktop.app import create_application
from athena.desktop.pathena_settings_comprehension_5100 import (
    apply_ui_refinements_5001_5100,
)
from athena.desktop.pathena_settings_runtime import (
    install_settings_runtime,
    model_storage_group,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-settings-runtime-test"])


def _model(model_id: str, *, loaded: bool = True) -> ModelResponse:
    return ModelResponse(
        provider="LM Studio",
        backend_model_id=model_id,
        display_name=model_id,
        model_type="llm",
        context_capacity=65_536,
        quantization="Q4",
        loaded=loaded,
        vision=False,
        trained_for_tool_use=True,
        loaded_context_length=65_536 if loaded else None,
    )


_DEFAULT_MODELS = (_model("Local Qwen"),)
_READY_PROVIDER = ProviderHealthResponse(
    provider="LM Studio",
    status="ready",
    detail=None,
)


def _snapshot(
    *,
    models: tuple[ModelResponse, ...] = _DEFAULT_MODELS,
    provider: ProviderHealthResponse | None = _READY_PROVIDER,
    core_status: str = "ok",
    model_error: str | None = None,
    model_freshness: SnapshotFreshness | None = None,
) -> DesktopApiSnapshot:
    return DesktopApiSnapshot(
        health=HealthResponse(
            api_version="v1",
            core_status=core_status,
            detail=None,
        ),
        provider=provider,
        models=models,
        chats=(),
        model_error=model_error,
        model_freshness=model_freshness,
    )


def _settings(tmp_path, name: str = "settings.ini") -> QSettings:
    return QSettings(str(tmp_path / name), QSettings.Format.IniFormat)


def _apply(
    window: PathenaMainWindow,
    runtime,
    snapshot: DesktopApiSnapshot,
) -> None:
    window.apply_api_snapshot(snapshot)
    runtime.apply_snapshot(snapshot)


def test_model_settings_persist_across_real_window_recreation(tmp_path) -> None:
    app = _app()
    snapshot = _snapshot()
    first = PathenaMainWindow(api_controller=None)
    first_runtime = install_settings_runtime(
        first,
        None,
        settings=_settings(tmp_path),
    )
    try:
        _apply(first, first_runtime, snapshot)
        first.context_spin.setValue(24_576)
        first.max_output_spin.setValue(2_048)
        first.temperature_spin.setValue(0.35)
        first.thinking_checkbox.setChecked(True)
        first_runtime.settings.sync()

        assert first._effective_context_limit() == 24_576
        assert first._max_output_tokens() == 2_048
        assert first._temperature() == pytest.approx(0.35)
        assert first._thinking_enabled() is True
        assert "saved locally" in first_runtime.persistence_value.text()
    finally:
        first.close()
        app.processEvents()

    second = PathenaMainWindow(api_controller=None)
    second_runtime = install_settings_runtime(
        second,
        None,
        settings=_settings(tmp_path),
    )
    try:
        _apply(second, second_runtime, snapshot)

        assert second._effective_context_limit() == 24_576
        assert second._max_output_tokens() == 2_048
        assert second._temperature() == pytest.approx(0.35)
        assert second._thinking_enabled() is True
        assert "restored locally" in second_runtime.persistence_value.text()
    finally:
        second.close()
        app.processEvents()


def test_persisted_values_remain_scoped_to_exact_model_id(tmp_path) -> None:
    app = _app()
    first_model = _model("provider/model-a")
    second_model = _model("provider/model-b")
    snapshot = _snapshot(models=(first_model, second_model))
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(window, None, settings=_settings(tmp_path))
    try:
        _apply(window, runtime, snapshot)
        window.context_spin.setValue(32_768)
        window.max_output_spin.setValue(4_096)

        second_index = window.model_selector.findData(second_model.backend_model_id)
        window.model_selector.setCurrentIndex(second_index)
        window._on_model_selected(second_index)
        runtime.hydrate_selected_model()
        window.context_spin.setValue(16_384)
        window.max_output_spin.setValue(1_024)

        first_index = window.model_selector.findData(first_model.backend_model_id)
        window.model_selector.setCurrentIndex(first_index)
        window._on_model_selected(first_index)
        runtime.hydrate_selected_model()

        assert window.context_spin.value() == 32_768
        assert window.max_output_spin.value() == 4_096
        assert model_storage_group(first_model.backend_model_id) != model_storage_group(
            second_model.backend_model_id
        )
    finally:
        window.close()
        app.processEvents()


def test_runtime_panel_never_turns_stale_or_missing_provider_into_ready(tmp_path) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(window, None, settings=_settings(tmp_path))
    apply_ui_refinements_5001_5100(window)
    comprehension = window.property("pathenaSettingsComprehensionController")
    try:
        ready = _snapshot()
        _apply(window, runtime, ready)
        comprehension.sync()
        assert runtime.provider_value.text() == "LM Studio · ready"
        assert runtime.provider_value.property("pathenaUiState") == "success"
        assert runtime.network_value.text() == "Local Core · connected"
        assert runtime.network_value.property("pathenaNetworkScope") == "loopback-only"
        assert runtime.network_value.accessibleName() == "Local Core connection"
        assert "does not indicate Internet access" in runtime.network_value.accessibleDescription()
        assert runtime.network_value.property("pathenaInternetStateInferred") is False

        stale = _snapshot(
            model_error="LM Studio model refresh timed out.",
            model_freshness="stale",
        )
        _apply(window, runtime, stale)
        assert runtime.provider_value.text() == "LM Studio · last known ready"
        assert runtime.provider_value.property("pathenaUiState") != "success"
        assert runtime.provider_value.property("pathenaRuntimeFreshness") == "stale"
        assert runtime.detail.text() == "LM Studio model refresh timed out."

        unavailable = _snapshot(
            models=(),
            provider=None,
            model_error="Provider could not be reached.",
            model_freshness="unavailable",
        )
        _apply(window, runtime, unavailable)
        comprehension.sync()
        assert runtime.provider_value.text() == "Model provider · unavailable"
        assert runtime.provider_value.property("pathenaUiState") == "error"
        assert "ready" not in runtime.provider_value.text().lower()
        assert "does not indicate Internet access" in runtime.network_value.accessibleDescription()
        assert runtime.network_value.property("pathenaInternetStateInferred") is False

        runtime.apply_connection_failure("Local Core refresh failed.")
        comprehension.sync()
        assert runtime.network_value.text() == "Local Core · unavailable"
        assert runtime.network_value.property("pathenaUiState") == "error"
        assert runtime.network_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.network_value.property("pathenaNetworkScope") == "unavailable"
        assert runtime.network_value.property("pathenaInternetStateInferred") is False
        assert "Internet-access state is not inferred" in runtime.network_value.accessibleDescription()
        assert "loopback" not in runtime.network_value.toolTip().lower()
    finally:
        window.close()
        app.processEvents()


def test_malformed_persisted_fields_do_not_replace_safe_defaults(tmp_path) -> None:
    app = _app()
    model = _model("Local Qwen")
    settings = _settings(tmp_path)
    settings.beginGroup(model_storage_group(model.backend_model_id))
    settings.setValue("model_id", model.backend_model_id)
    settings.setValue("context_tokens", "not-an-integer")
    settings.setValue("max_output_tokens", -1)
    settings.setValue("temperature", "nan")
    settings.setValue("thinking", "sometimes")
    settings.endGroup()
    settings.sync()

    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(window, None, settings=settings)
    try:
        _apply(window, runtime, _snapshot(models=(model,)))

        assert window.context_spin.value() == 65_536
        assert window.max_output_spin.value() == 8_192
        assert window.temperature_spin.value() == pytest.approx(0.7)
        assert window.thinking_checkbox.isChecked() is False
        assert "invalid local values" in runtime.persistence_value.text()
        assert runtime.persistence_value.property("pathenaUiState") == "error"
    finally:
        window.close()
        app.processEvents()


def test_real_controller_snapshot_signal_drives_settings_runtime(tmp_path) -> None:
    app = _app()
    controller = DesktopApiController(object())  # type: ignore[arg-type]
    window = PathenaMainWindow(api_controller=controller)
    runtime = install_settings_runtime(window, controller, settings=_settings(tmp_path))
    try:
        controller.snapshot_ready.emit(_snapshot())

        assert runtime.provider_value.text() == "LM Studio · ready"
        assert runtime.network_value.text() == "Local Core · connected"
        assert window.model_selector.currentData() == "Local Qwen"
        assert runtime.panel.parentWidget() is window.pages.widget(6)
    finally:
        window.refresh_timer.stop()
        window.close()
        app.processEvents()
