from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from athena.desktop.app import create_application  # noqa: E402
from athena.desktop.command_palette import CommandPaletteController  # noqa: E402
from athena.desktop.pathena_capability_catalog import (  # noqa: E402
    CapabilityAvailability,
    resolve_capability_catalog,
)
from athena.desktop.pathena_pallas_command import install_pallas_command  # noqa: E402
from athena.desktop.pathena_pallas_field import install_pallas_grounded_field  # noqa: E402
from athena.desktop.pathena_pallas_full_view import install_pallas_full_view  # noqa: E402
from athena.desktop.pathena_window import PathenaMainWindow  # noqa: E402


def test_open_pallas_command_uses_installed_synchronized_full_view() -> None:
    app = create_application(["pathena-pallas-command-test"])
    window = PathenaMainWindow(api_controller=None)
    grounded = install_pallas_grounded_field(window, None)
    full_view = install_pallas_full_view(window, grounded)
    palette = CommandPaletteController(window)
    try:
        assert install_pallas_command(palette) is True
        assert window.property("pathenaPallasCommandInstalled") is True

        commands = [command for command in palette._commands if command.label == "Open PALLAS"]
        assert len(commands) == 1

        snapshot = resolve_capability_catalog(window, palette._commands)
        capability = next(item for item in snapshot.capabilities if item.label == "Open PALLAS")
        assert capability.availability is CapabilityAvailability.AVAILABLE
        assert snapshot.has_drift is False

        commands[0].action()
        app.processEvents()
        assert full_view.dialog is not None
        assert full_view.workspace is not None
        assert full_view.dialog.isVisible()

        assert install_pallas_command(palette) is True
        assert sum(command.label == "Open PALLAS" for command in palette._commands) == 1
    finally:
        full_view.dispose()
        palette.deleteLater()
        grounded.deleteLater()
        window.close()
        app.processEvents()
