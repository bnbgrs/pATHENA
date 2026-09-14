from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from athena.desktop.app import create_application  # noqa: E402
from athena.desktop.command_palette import CommandPaletteController  # noqa: E402
from athena.desktop.pathena_capability_catalog import (  # noqa: E402
    CAPABILITY_METADATA,
    resolve_capability_catalog,
)
from athena.desktop.pathena_window import PathenaMainWindow  # noqa: E402


def test_sources_is_the_user_facing_name_for_workspace_row_four() -> None:
    app = create_application(["pathena-sources-command-test"])
    window = PathenaMainWindow(api_controller=None)
    palette = CommandPaletteController(window)
    try:
        labels = [command.label for command in palette._commands]
        assert "Open Sources" in labels
        assert "Open Files" not in labels
        assert "Open Sources" in CAPABILITY_METADATA
        assert "Open Files" not in CAPABILITY_METADATA

        command = next(command for command in palette._commands if command.label == "Open Sources")
        command.action()
        assert window.navigation.currentRow() == 4

        snapshot = resolve_capability_catalog(window, palette._commands)
        assert snapshot.has_drift is False
    finally:
        palette.deleteLater()
        window.close()
        app.processEvents()
