from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.command_palette import install_command_palette
from athena.desktop.pathena_comfyui import COMFYUI_URL_ENV
from athena.desktop.pathena_command_palette_truth_6500 import (
    install_command_palette_truth,
)
from athena.desktop.pathena_external_workspaces import install_external_workspaces
from athena.desktop.pathena_pallas_field import install_pallas_grounded_field
from athena.desktop.pathena_pallas_full_view import install_pallas_full_view
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-optional-comfyui-startup-test"])


def test_invalid_optional_comfyui_config_stays_fail_closed_through_command_truth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(COMFYUI_URL_ENV, "https://example.com:8188")
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    grounded = install_pallas_grounded_field(window)
    pallas = install_pallas_full_view(window, grounded)
    palette = install_command_palette(window)

    external = install_external_workspaces(window, palette, pallas)
    truth = install_command_palette_truth(palette)
    window.show()
    app.processEvents()

    labels = {command.label for command in palette._commands}  # noqa: SLF001
    assert external.comfyui is None
    assert "Open ComfyUI" not in labels
    assert window.property("pathenaComfyUiInstalled") is False
    assert "local HTTP" in str(window.property("pathenaComfyUiUnavailableReason"))
    assert window.property("pathenaCommandPaletteTruthManaged") is True

    external.dispose()
    external.deleteLater()
    truth.deleteLater()
    pallas.dispose()
    pallas.deleteLater()
    palette.dialog.deleteLater()
    palette.help_dialog.deleteLater()
    palette.deleteLater()
    grounded.deleteLater()
    window.close()
