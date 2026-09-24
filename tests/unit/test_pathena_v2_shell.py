from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame

from athena.desktop.pathena_v2_shell import install_v2_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_shell_recomposes_real_window_without_changing_route_contract() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v2_shell(window)

    shell = window.centralWidget()
    assert shell is not None
    assert shell.objectName() == "v2Shell"
    assert shell.findChild(QFrame, "referenceBody") is not None
    assert shell.findChild(QFrame, "conversation") is not None
    assert shell.findChild(QFrame, "legacyReferenceBody") is not None

    assert window.pages.count() == 7
    assert window.pages.widget(0).objectName() == "v2ChatPage"
    assert window.prompt_input.parent().objectName() == "v2Composer"

    sidebar = shell.findChild(QFrame, "v2Sidebar")
    assert sidebar is not None
    assert sidebar.width() == 204
    assert all(
        not button.icon().isNull()
        for button in (*controller._nav_buttons.values(), controller._pallas_button)
    )

    inactive_icon = controller._nav_buttons[2].icon().cacheKey()
    window.navigation.setCurrentRow(2)
    assert window.pages.currentIndex() == 2
    assert controller._nav_buttons[2].property("active") is True
    assert controller._nav_buttons[0].property("active") is False
    assert controller._nav_buttons[2].icon().cacheKey() != inactive_icon

    window.close()


def test_v2_shell_binds_existing_command_palette_contract() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v2_shell(window)
    called: list[str] = []

    controller.bind_command_palette(lambda: called.append("open"))
    assert controller._command_button.isEnabled()
    controller._command_button.click()

    assert called == ["open"]
    window.close()



def test_v2_finalize_recomposes_settings_without_replacing_real_controls() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v2_shell(window)

    model_selector = window.settings_model_selector
    context_slider = window.context_slider
    context_spin = window.context_spin
    output_slider = window.max_output_slider
    output_spin = window.max_output_spin
    temperature = window.temperature_spin
    thinking = window.thinking_checkbox

    controller.finalize()

    settings = window.pages.widget(6)
    assert settings is not None
    assert settings.objectName() == "v2SettingsPage"
    assert model_selector.parent() is not None
    assert settings.isAncestorOf(model_selector)
    assert settings.isAncestorOf(context_slider)
    assert settings.isAncestorOf(context_spin)
    assert settings.isAncestorOf(output_slider)
    assert settings.isAncestorOf(output_spin)
    assert settings.isAncestorOf(temperature)
    assert settings.isAncestorOf(thinking)
    assert window.pages.count() == 7

    window.navigation.setCurrentRow(6)
    assert window.pages.currentWidget() is settings
    assert controller._nav_buttons[6].property("active") is True

    window.close()



def test_v2_pallas_has_first_class_active_navigation_state() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v2_shell(window)

    window.navigation.setCurrentRow(2)
    assert controller._nav_buttons[2].property("active") is True

    controller.pallas_opened()
    assert controller._pallas_button.property("active") is True
    assert all(
        button.property("active") is False
        for button in controller._nav_buttons.values()
    )

    controller.pallas_closed()
    assert controller._pallas_button.property("active") is False
    assert controller._nav_buttons[2].property("active") is True

    window.close()
