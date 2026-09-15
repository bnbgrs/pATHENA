from __future__ import annotations

import os
from tempfile import TemporaryDirectory

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings  # noqa: E402

from athena.desktop.app import create_application  # noqa: E402
from athena.desktop.pathena_secondary_navigation import (  # noqa: E402
    install_settings_secondary_navigation,
)
from athena.desktop.pathena_settings_runtime import install_settings_runtime  # noqa: E402
from athena.desktop.pathena_window import PathenaMainWindow  # noqa: E402


def test_settings_reference_rail_uses_only_real_sections() -> None:
    app = create_application(["pathena-settings-reference-test"])
    window = PathenaMainWindow(api_controller=None)
    with TemporaryDirectory() as directory:
        settings = QSettings(f"{directory}/settings.ini", QSettings.Format.IniFormat)
        runtime = install_settings_runtime(window, None, settings=settings)
        navigation = install_settings_secondary_navigation(window)
        try:
            assert navigation.section_names == ("Models & inference", "System status")
            assert navigation.navigation.count() == 2
            assert navigation.navigation.property("referenceFamily") == "11-screen-2026-08-24"
            assert navigation.container.property("referenceFamily") == "11-screen-2026-08-24"

            labels = [
                navigation.navigation.item(index).text()
                for index in range(navigation.navigation.count())
            ]
            assert labels == ["Models & inference", "System status"]
            assert not {"General", "Privacy", "Network", "Appearance", "Knowledge", "Advanced"}.intersection(labels)

            style = navigation.navigation.styleSheet()
            assert "border-right:" in style
            assert "background: transparent;" in style
        finally:
            navigation.deleteLater()
            runtime.deleteLater()
            window.close()
            app.processEvents()
