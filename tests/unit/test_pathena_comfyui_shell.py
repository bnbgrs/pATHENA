from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QFrame

from athena.desktop.app import create_application
from athena.desktop.command_palette import install_command_palette
from athena.desktop.pathena_comfyui import install_comfyui_integration
from athena.desktop.pathena_comfyui_shell import install_comfyui_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _surface():
    app = create_application(["pathena-comfyui-shell-test"])
    window = PathenaMainWindow(api_controller=None)
    palette = install_command_palette(window)
    comfyui = install_comfyui_integration(palette)
    shell = install_comfyui_shell(palette, comfyui)
    window.resize(1480, 900)
    window.show()
    app.processEvents()
    return app, window, palette, comfyui, shell


def test_comfyui_open_is_shell_hosted_without_changing_primary_routes() -> None:
    app, window, _palette, comfyui, shell = _surface()
    center = window.findChild(QFrame, "conversation")
    reference_body = window.findChild(QFrame, "referenceBody")
    assert center is not None and center.isVisible()
    assert reference_body is not None
    assert shell.surface.parentWidget() is reference_body
    assert shell.surface.property("pathenaComfyUiShellHosted") is True
    assert comfyui.dialog.property("pathenaComfyUiLocalOnly") is True
    assert window.navigation.count() == 7
    assert window.pages.count() == 7

    comfyui.open()
    app.processEvents()

    assert shell.is_open
    assert shell.surface.isVisible()
    assert not center.isVisible()
    assert window.property("pathenaComfyUiShellOpen") is True
    assert window.isVisible()
    assert window.navigation.count() == 7
    assert window.pages.count() == 7

    shell.dispose()
    window.close()


def test_navigation_restores_routed_workspace_from_comfyui() -> None:
    app, window, _palette, comfyui, shell = _surface()
    center = window.findChild(QFrame, "conversation")
    assert center is not None

    comfyui.open()
    app.processEvents()
    assert shell.is_open
    assert not center.isVisible()

    window.navigation.setCurrentRow(1)
    app.processEvents()

    assert window.pages.currentIndex() == 1
    assert not shell.is_open
    assert not shell.surface.isVisible()
    assert center.isVisible()
    assert window.property("pathenaComfyUiShellOpen") is False

    shell.dispose()
    window.close()


def test_open_comfyui_command_targets_shell_host() -> None:
    app, window, palette, _comfyui, shell = _surface()
    command = next(command for command in palette._commands if command.label == "Open ComfyUI")

    command.action()
    app.processEvents()

    assert shell.is_open
    assert shell.surface.isVisible()
    assert window.property("pathenaComfyUiShellOpen") is True

    shell.dispose()
    window.close()
