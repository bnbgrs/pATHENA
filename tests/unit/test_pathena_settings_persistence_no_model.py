from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.pathena_settings_runtime import install_settings_runtime
from athena.desktop.pathena_window import PathenaMainWindow


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
