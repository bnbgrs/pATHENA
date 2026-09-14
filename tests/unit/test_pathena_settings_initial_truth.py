from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.pathena_settings_runtime import install_settings_runtime
from athena.desktop.pathena_window import PathenaMainWindow


def _runtime(tmp_path):
    app = create_application(["pathena-settings-initial-truth-test"])
    window = PathenaMainWindow(api_controller=None)
    runtime = install_settings_runtime(
        window,
        None,
        settings=QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    return app, window, runtime


def test_pre_first_snapshot_runtime_state_fails_closed(tmp_path) -> None:
    app, window, runtime = _runtime(tmp_path)
    try:
        assert runtime.provider_value.text() == "Model provider · awaiting Core"
        assert runtime.provider_value.property("pathenaUiState") == "idle"
        assert runtime.provider_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.provider_value.accessibleDescription() == runtime.provider_value.text()

        assert runtime.network_value.text() == "Local Core · awaiting connection"
        assert runtime.network_value.property("pathenaUiState") == "idle"
        assert runtime.network_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.network_value.property("pathenaNetworkScope") == "unavailable"
        assert runtime.network_value.property("pathenaInternetStateInferred") is False
    finally:
        window.close()
        app.processEvents()


def test_initial_persistence_state_reports_unavailable_freshness(tmp_path) -> None:
    app, window, runtime = _runtime(tmp_path)
    try:
        assert runtime.persistence_value.text() == "Per-model settings · not saved yet"
        assert runtime.persistence_value.property("pathenaUiState") == "idle"
        assert runtime.persistence_value.property("pathenaRuntimeFreshness") == "unavailable"
        assert runtime.persistence_value.accessibleDescription() == runtime.persistence_value.text()
    finally:
        window.close()
        app.processEvents()
