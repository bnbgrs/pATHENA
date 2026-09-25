from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_comfyui import ComfyUiClient, install_comfyui_integration
from athena.desktop.pathena_v2_shell import install_v2_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-v2-comfyui-test"])


class _PallasStub(QObject):
    workspace_opened = Signal()


def test_v2_comfyui_is_shell_hosted_and_restores_selected_route() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    shell = install_v2_shell(window)
    pallas = _PallasStub(window)
    pallas.workspace_opened.connect(shell.pallas_opened)
    window.__dict__["_pathena_pallas_full_view_controller"] = pallas
    palette = CommandPaletteController(window)
    controller = install_comfyui_integration(
        palette,
        client=ComfyUiClient("http://127.0.0.1:8188"),
    )
    window.show()
    app.processEvents()

    try:
        assert controller.dialog.isHidden()
        assert window.navigation.currentRow() == 0
        assert window.pages.currentIndex() == 0
        title = window.findChild(QLabel, "v2PageTitle")
        assert title is not None
        assert title.text() == "Chat"

        window.navigation.setCurrentRow(6)
        app.processEvents()

        workspace = window.findChild(QWidget, "v2Workspace")
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
        inspector = window.findChild(QWidget, "inspector")
        assert inspector is not None
        assert inspector.isHidden()
        assert window.navigation.currentRow() == 6
        assert window.pages.currentIndex() == selected_page
        assert title.text() == "ComfyUI"
        assert hint.text() == "Local image and video workflows · loopback only."
        assert controller.close_button.isVisible()
        assert app.focusWidget() is controller.check_button

        window.resize(window.width() + 180, window.height() + 120)
        app.processEvents()
        assert controller.dialog.geometry() == workspace.rect()

        window.navigation.setCurrentRow(1)
        app.processEvents()
        assert controller.dialog.isHidden()
        assert window.pages.currentIndex() == 1
        assert title.text() == "Knowledge"

        window.navigation.setCurrentRow(6)
        controller.open()
        app.processEvents()
        assert controller.dialog.isVisible()
        assert title.text() == "ComfyUI"

        window.setProperty("pathenaPallasShellOpen", True)
        pallas.workspace_opened.emit()
        app.processEvents()

        assert controller.dialog.isHidden()
        pallas_button = window.findChild(QWidget, "v2PallasButton")
        assert pallas_button is not None
        assert pallas_button.property("active") is True
        assert title.text() == "PALLAS"
        assert hint.text() == "Living semantic workspace"

        window.setProperty("pathenaPallasShellOpen", False)
        shell.pallas_closed()
        controller.open()
        app.processEvents()
        assert controller.dialog.isVisible()
        assert title.text() == "ComfyUI"

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
