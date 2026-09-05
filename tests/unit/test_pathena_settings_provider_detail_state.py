from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from athena.api.contracts import HealthResponse, ProviderHealthResponse
from athena.desktop.api_controller import DesktopApiSnapshot
from athena.desktop.app import create_application
from athena.desktop.pathena_settings_runtime import install_settings_runtime
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-settings-provider-detail-state-test"])


def test_fresh_non_ready_provider_detail_is_presented_as_error(tmp_path) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="LM Studio",
            status="error",
            detail="Local provider reported an error.",
        ),
        models=(),
        chats=(),
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.provider_value.text() == "LM Studio · error"
        assert runtime.provider_value.property("pathenaUiState") == "error"
        assert runtime.provider_value.property("pathenaRuntimeFreshness") == "fresh"
        assert runtime.detail.text() == "Local provider reported an error."
        assert runtime.detail.property("pathenaUiState") == "error"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "fresh"
        assert runtime.detail.accessibleDescription() == runtime.detail.text()
    finally:
        window.close()
        app.processEvents()


def test_unavailable_provider_detail_fails_closed_as_error(tmp_path) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=None,
        models=(),
        chats=(),
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.provider_value.text() == "Model provider · unavailable"
        assert runtime.provider_value.property("pathenaUiState") == "error"
        assert runtime.provider_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.detail.text() == (
            "Model provider is unavailable in the local Core snapshot."
        )
        assert runtime.detail.property("pathenaUiState") == "error"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.detail.accessibleDescription() == runtime.detail.text()
    finally:
        window.close()
        app.processEvents()
