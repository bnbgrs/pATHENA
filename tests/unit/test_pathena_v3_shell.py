from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame

from athena.desktop.pathena_v3_shell import install_v3_shell
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_v3_shell_is_structurally_distinct_and_keeps_route_contract() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)

    shell = window.centralWidget()
    assert shell is not None
    assert shell.objectName() == "v3Shell"
    assert shell.findChild(QFrame, "referenceBody") is not None
    assert shell.findChild(QFrame, "conversation") is not None
    assert shell.findChild(QFrame, "v2Sidebar") is None

    rail = shell.findChild(QFrame, "v3Rail")
    assert rail is not None
    assert rail.width() == 70
    assert all(
        button.text() == ""
        for button in (*controller._nav_buttons.values(), controller._pallas_button)
    )
    assert all(
        not button.icon().isNull()
        for button in (*controller._nav_buttons.values(), controller._pallas_button)
    )

    assert window.pages.count() == 7
    assert window.pages.widget(0).objectName() == "v3ChatPage"
    assert window.prompt_input.parent().objectName() == "v3Composer"

    window.navigation.setCurrentRow(2)
    assert window.pages.currentIndex() == 2
    assert controller._nav_buttons[2].property("active") is True
    assert controller._nav_buttons[0].property("active") is False

    window.close()


def test_v3_shell_keeps_real_command_and_pallas_entry_points() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    calls: list[str] = []

    controller.bind_command_palette(lambda: calls.append("command"))
    controller.bind_pallas(lambda: calls.append("pallas"))

    window.show()
    controller._command_button.setFocus(Qt.FocusReason.TabFocusReason)
    QApplication.processEvents()
    controller._command_button.click()
    controller._pallas_button.click()

    assert calls == ["command", "pallas"]
    controller.pallas_opened()
    assert controller._pallas_button.property("active") is True
    assert all(
        button.property("active") is False
        for button in controller._nav_buttons.values()
    )
    controller.pallas_closed()

    window.close()


def test_v3_finalize_reuses_real_settings_controls() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)

    real_controls = (
        window.settings_model_selector,
        window.context_slider,
        window.context_spin,
        window.max_output_slider,
        window.max_output_spin,
        window.temperature_spin,
        window.thinking_checkbox,
    )

    controller.finalize()

    settings = window.pages.widget(6)
    assert settings is not None
    assert settings.objectName() == "v3SettingsPage"
    assert all(settings.isAncestorOf(control) for control in real_controls)
    assert window.pages.count() == 7

    window.navigation.setCurrentRow(6)
    assert window.pages.currentWidget() is settings
    assert controller._nav_buttons[6].property("active") is True

    window.close()


def test_v3_send_affordance_survives_busy_cycle() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    window.setProperty("pathenaV3Presentation", True)
    install_v3_shell(window)

    assert window.send_button.text() == "↑"
    window.apply_chat_busy(True)
    assert window.send_button.text() == "…"
    window.apply_chat_busy(False)
    assert window.send_button.text() == "↑"

    window.close()


def test_v3_theme_exposes_keyboard_focus_and_readable_dim_text() -> None:
    assert 'QPushButton[v3Nav="true"]:focus' in PATHENA_V3_STYLESHEET
    assert "QPushButton#sendButton:focus" in PATHENA_V3_STYLESHEET
    assert "QLineEdit#promptInput:focus" in PATHENA_V3_STYLESHEET
    assert "#817D87" in PATHENA_V3_STYLESHEET
