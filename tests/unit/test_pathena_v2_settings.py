from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_v2_settings import install_v2_settings
from athena.desktop.pathena_v2_shell import install_v2_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v2_settings_reuses_real_controls_and_preserves_route_contract() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    install_v2_shell(window)

    old_settings = window.pages.widget(6)
    assert old_settings is not None
    runtime_panel = old_settings.findChild(QWidget, "settingsRuntimePanel")

    model_selector = window.settings_model_selector
    context_slider = window.context_slider
    context_spin = window.context_spin
    output_slider = window.max_output_slider
    output_spin = window.max_output_spin
    temperature = window.temperature_spin
    thinking = window.thinking_checkbox

    controller = install_v2_settings(window)

    settings = window.pages.widget(6)
    assert settings is controller.page
    assert settings is not None
    assert settings.objectName() == "v2SettingsPage"
    assert window.pages.count() == 7

    for control in (
        model_selector,
        context_slider,
        context_spin,
        output_slider,
        output_spin,
        temperature,
        thinking,
    ):
        assert settings.isAncestorOf(control)

    if runtime_panel is not None:
        assert settings.isAncestorOf(runtime_panel)
        assert runtime_panel.objectName() == "v2SettingsRuntimePanel"

    window.navigation.setCurrentRow(6)
    assert window.pages.currentWidget() is settings

    window.close()


def test_v2_settings_section_navigation_is_local_and_truthful() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    install_v2_shell(window)
    controller = install_v2_settings(window)

    assert len(controller.section_buttons) == 2
    assert controller.current_section == 0
    assert controller.section_buttons[0].property("active") is True
    assert controller.section_buttons[1].property("active") is False

    controller.section_buttons[1].click()

    assert controller.current_section == 1
    assert controller.section_buttons[0].property("active") is False
    assert controller.section_buttons[1].property("active") is True

    controller.set_section(99)
    assert controller.current_section == 1

    window.close()


def test_v2_settings_install_is_idempotent_and_shell_finalize_does_not_replace_it() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    shell_controller = install_v2_shell(window)

    first = install_v2_settings(window)
    page = first.page
    second = install_v2_settings(window)

    assert second is first
    assert window.pages.widget(6) is page

    shell_controller.finalize()

    assert window.pages.widget(6) is page
    assert window.pages.count() == 7

    window.close()
