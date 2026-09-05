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


def test_model_snapshot_failure_keeps_provider_as_last_known(tmp_path) -> None:
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
            status="ready",
            detail=None,
        ),
        models=(),
        chats=(),
        model_error="ATHENA model list refresh failed.",
        model_freshness="unavailable",
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.provider_value.text() == "LM Studio · last known ready"
        assert runtime.provider_value.property("pathenaUiState") == "idle"
        assert runtime.provider_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.provider_value.accessibleDescription() == runtime.provider_value.text()
        assert runtime.detail.text() == "ATHENA model list refresh failed."
        assert runtime.detail.property("pathenaUiState") == "error"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "unavailable"
    finally:
        window.close()
        app.processEvents()


def test_blank_provider_identity_and_status_use_self_describing_copy(tmp_path) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(provider="   ", status="", detail=None),
        models=(),
        chats=(),
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.provider_value.text() == "Model provider · unavailable"
        assert runtime.provider_value.property("pathenaUiState") == "error"
        assert runtime.provider_value.property("pathenaRuntimeFreshness") == "fresh"
        assert runtime.provider_value.accessibleDescription() == runtime.provider_value.text()
        assert runtime.detail.property("pathenaUiState") == "error"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "fresh"
    finally:
        window.close()
        app.processEvents()


@pytest.mark.parametrize("core_status", ["", "   "])
def test_empty_core_status_uses_self_describing_unavailable_copy(
    tmp_path, core_status: str
) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status=core_status, detail=None),
        provider=None,
        models=(),
        chats=(),
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.network_value.text() == "Local Core · unavailable"
        assert runtime.network_value.property("pathenaUiState") == "error"
        assert runtime.network_value.property("pathenaRuntimeFreshness") == "fresh"
        assert runtime.network_value.property("pathenaNetworkScope") == "loopback-only"
        assert runtime.network_value.property("pathenaInternetStateInferred") is False
        assert runtime.network_value.accessibleDescription().startswith(
            "Local Core · unavailable."
        )
    finally:
        window.close()
        app.processEvents()


@pytest.mark.parametrize("message", ["", "   "])
def test_empty_connection_failure_detail_uses_self_describing_fallback(
    tmp_path, message: str
) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    try:
        runtime.apply_connection_failure(message)

        assert runtime.detail.text() == "Local Core connection failed."
        assert runtime.detail.property("pathenaUiState") == "error"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.detail.accessibleDescription() == runtime.detail.text()
    finally:
        window.close()
        app.processEvents()


def test_nonempty_connection_failure_detail_is_preserved(tmp_path) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    try:
        runtime.apply_connection_failure("Core handshake failed.")

        assert runtime.detail.text() == "Core handshake failed."
        assert runtime.detail.accessibleDescription() == runtime.detail.text()
    finally:
        window.close()
        app.processEvents()


@pytest.mark.parametrize("detail", [" ", "\t", "\r\n"])
def test_whitespace_provider_detail_uses_self_describing_fallback(
    tmp_path, detail: str
) -> None:
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
            status="ready",
            detail=detail,
        ),
        models=(),
        chats=(),
    )
    fallback = (
        "Provider readiness is reported by the local Core; no remote status "
        "or unsupported capability is inferred."
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.detail.text() == fallback
        assert runtime.detail.accessibleDescription() == fallback
        assert runtime.detail.property("pathenaUiState") == "idle"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "fresh"
    finally:
        window.close()
        app.processEvents()


def test_nonblank_provider_detail_is_preserved_verbatim(tmp_path) -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    detail = "  Provider is ready with local metadata.  "
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="LM Studio",
            status="ready",
            detail=detail,
        ),
        models=(),
        chats=(),
    )
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.detail.text() == detail
        assert runtime.detail.accessibleDescription() == detail
        assert runtime.detail.property("pathenaUiState") == "idle"
        assert runtime.detail.property("pathenaRuntimeFreshness") == "fresh"
    finally:
        window.close()
        app.processEvents()
