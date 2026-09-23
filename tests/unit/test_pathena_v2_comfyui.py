from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QWidget

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_comfyui import ComfyUiClient, install_comfyui_integration
from athena.desktop.pathena_v2_shell import install_v2_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-v2-comfyui-test"])


def test_v2_comfyui_is_shell_hosted_and_restores_selected_route() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    install_v2_shell(window)
    palette = CommandPaletteController(window)
    controller = install_comfyui_integration(
        palette,
        client=ComfyUiClient("http://127.0.0.1:8188"),
    )
    window.show()
    app.processEvents()

    try:
        window.navigation.setCurrentRow(6)
        app.processEvents()

        workspace = window.findChild(QWidget, "v2Workspace")
        title = window.findChild(QLabel, "v2PageTitle")
        hint = window.findChild(QLabel, "v2PageHint")
        assert workspace is not None
        assert title is not None
        assert hint is not None
        assert title.text() == "Settings"
        selected_page = window.pages.currentIndex()

        controller.open()
        app.processEvents()

        assert controller.dialog.isVisible()
        assert controller.dialog.parent() is workspace
        assert controller.dialog.property("pathenaShellHosted") is True
        assert controller.dialog.property("pathenaComfyUiShellHosted") is True
        assert controller.dialog.geometry() == workspace.rect()
        assert window.navigation.currentRow() == 6
        assert window.pages.currentIndex() == selected_page
        assert title.text() == "ComfyUI"
        assert hint.text() == "Local image and video workflows · loopback only."
        assert controller.close_button.isVisible()
        assert app.focusWidget() is controller.check_button

        controller.close_button.click()
        app.processEvents()

        assert not controller.dialog.isVisible()
        assert window.navigation.currentRow() == 6
        assert window.pages.currentIndex() == selected_page
        assert title.text() == "Settings"
        assert hint.text() != "Local image and video workflows · loopback only."
    finally:
        controller.dialog.hide()
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()
