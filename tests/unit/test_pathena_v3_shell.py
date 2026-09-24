from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame

from athena.desktop.pathena_v3_shell import install_v3_shell
from athena.desktop.pathena_v3_system import install_v3_system_workspace
from athena.desktop.pathena_v3_theme import PATHENA_V3_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace


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
    assert window.chat_selector.currentText() == "CONNECTING…"
    assert window.model_selector.currentText() == "CONNECTING…"

    window.navigation.setCurrentRow(2)
    assert window.pages.currentIndex() == 2
    assert controller._nav_buttons[2].property("active") is True
    assert controller._nav_buttons[0].property("active") is False

    window.close()


def test_v3_chat_workspace_keeps_readable_center_width() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    install_v3_shell(window)

    window.resize(1440, 900)
    window.show()
    app.processEvents()

    stage = window.findChild(QFrame, "v3ConversationStage")
    composer = window.findChild(QFrame, "v3Composer")
    assert stage is not None
    assert composer is not None
    assert stage.width() >= 760
    assert window.chat_scroll.width() >= 680
    assert window.chat_messages_widget.width() >= 640
    assert composer.width() >= 760

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
    assert controller._command_button.hasFocus()
    controller._command_button.click()

    controller._nav_buttons[1].setFocus(Qt.FocusReason.TabFocusReason)
    QApplication.processEvents()
    assert controller._nav_buttons[1].hasFocus()

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


def test_v3_legacy_inspector_cannot_reopen_on_non_chat_route() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    window.setProperty("pathenaV3Presentation", True)
    install_v3_shell(window)

    window.show()
    window.navigation.setCurrentRow(6)
    app.processEvents()

    inspector = window.findChild(QFrame, "inspector")
    assert inspector is not None

    # Exercise the legacy visibility path explicitly: V3 owns contextual
    # visibility and must not regain the old always-on side panel.
    window._sync_inspector_visibility()
    app.processEvents()
    assert inspector.isHidden()

    window.close()


def test_v3_styles_close_system_and_context_surface_drift() -> None:
    assert "QTabWidget#systemOperationsTabs::pane" in PATHENA_V3_STYLESHEET
    assert "QWidget#backupWorkspace" in PATHENA_V3_STYLESHEET
    assert "QFrame#inspectorRouteContext" in PATHENA_V3_STYLESHEET
    assert "QDialog#helpWorkspace" in PATHENA_V3_STYLESHEET
    assert 'QPushButton[v3Nav="true"]:focus' in PATHENA_V3_STYLESHEET
    assert "QPushButton#v3CommandButton:focus" in PATHENA_V3_STYLESHEET
    assert "QCheckBox:focus" in PATHENA_V3_STYLESHEET
    assert "QListWidget:focus" in PATHENA_V3_STYLESHEET


def test_v3_system_transition_never_restores_legacy_inspector() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    window.setProperty("pathenaV3Presentation", True)
    install_v3_shell(window)
    system = install_system_workspace(window, None)
    install_system_backup(window, system)
    install_v3_system_workspace(system)

    window.show()
    window.navigation.setCurrentRow(5)
    app.processEvents()

    inspector = window.findChild(QFrame, "inspector")
    assert inspector is not None
    assert inspector.isHidden()

    # Leaving Runtime fires SystemWorkspace.hideEvent(). V3 must not inherit
    # the legacy behavior that reopened the global Evidence & Activity panel.
    window.navigation.setCurrentRow(6)
    app.processEvents()
    assert inspector.isHidden()

    window.close()
