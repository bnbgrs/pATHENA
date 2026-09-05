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


_FALLBACK = (
    "Provider readiness is reported by the local Core; no remote status "
    "or unsupported capability is inferred."
)


def _app() -> QApplication:
    return create_application(["pathena-settings-provider-detail-whitespace-test"])


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
    try:
        runtime.apply_snapshot(snapshot)

        assert runtime.detail.text() == _FALLBACK
        assert runtime.detail.accessibleDescription() == _FALLBACK
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
