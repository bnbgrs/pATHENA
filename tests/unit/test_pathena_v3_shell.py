from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPlainTextEdit, QToolButton

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

    assert controller._header.height() == 68
    assert "#78D1C5" in PATHENA_V3_STYLESHEET
    assert "#7C9CFF" not in PATHENA_V3_STYLESHEET
    assert (
        'QToolButton[v3Nav="true"]:focus {\n'
        "    color: #D7DBDF;\n"
        "    background: #14181D;\n"
        "    border-color: #3B4652;"
        in PATHENA_V3_STYLESHEET
    )
    assert "QFrame#v3ChatMeta {\n    background: transparent;" in PATHENA_V3_STYLESHEET
    assert "QFrame#v3ControlRow {\n    background: transparent;" in PATHENA_V3_STYLESHEET

    rail = shell.findChild(QFrame, "v3Rail")
    assert rail is not None
    assert 76 <= rail.width() <= 80
    assert rail.minimumWidth() == rail.maximumWidth()

    nav_buttons = shell.findChildren(QToolButton, "v3NavButton")
    assert all(button.width() <= rail.width() - 14 for button in nav_buttons)
    assert [button.text() for button in nav_buttons[:5]] == [
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Sources",
    ]
    assert [button.text() for button in controller._nav_buttons.values()] == [
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    ]
    assert controller._pallas_button.text() == "PALLAS"
    assert all(
        not button.icon().isNull()
        for button in (*controller._nav_buttons.values(), controller._pallas_button)
    )

    assert window.pages.count() == 7
    assert window.pages.widget(0).objectName() == "v3ChatPage"
    assert window.prompt_input.parent().objectName() == "v3Composer"
    assert isinstance(window.prompt_input, QPlainTextEdit)
    assert window.prompt_input.minimumHeight() == 56
    assert window.prompt_input.maximumHeight() == 120
    window.prompt_input.setText("first line\nsecond line")
    assert window.prompt_input.text() == "first line\nsecond line"

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
    assert controller._command_button.hasFocus()
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


def test_v3_non_chat_routes_cannot_resurrect_legacy_inspector() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    controller.finalize()

    inspector = window.findChild(QFrame, "inspector")
    assert inspector is not None

    window.navigation.setCurrentRow(6)
    app.processEvents()
    assert inspector.isHidden()

    # Late Core/context refreshes still call the base visibility synchronizer.
    # V3 must keep the legacy inspector out of non-chat workspaces.
    window._sync_inspector_visibility()
    app.processEvents()
    assert inspector.isHidden()

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


def test_v3_shell_keeps_core_chat_controls_visible_at_minimum_desktop_size() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = install_v3_shell(window)
    controller.finalize()

    window.resize(1120, 720)
    window.show()
    app.processEvents()

    try:
        assert window.size().width() >= 1120
        assert window.size().height() >= 720
        assert window.model_selector.isVisible()
        assert window.chat_selector.isVisible()
        assert window.chat_selector.accessibleName() == "Conversation"
        assert window.model_selector.accessibleName() == "Local model"
        assert window.new_chat_button.accessibleName() == "New conversation"
        assert window.delete_chat_button.accessibleName() == "Delete conversation"
        assert window.prompt_input.isVisible()
        assert window.prompt_input.maximumHeight() == 120
        assert window.ground_button.isVisible()
        assert window.send_button.isVisible()
        assert window.send_button.width() == 44
        assert window.send_button.height() == 44
        assert window.ground_button.text() == "Sources"
        assert window.send_button.text() == "↑"
        assert "color: rgba(0, 0, 0, 0)" in window.ground_button.styleSheet()
        assert "color: rgba(0, 0, 0, 0)" in window.send_button.styleSheet()
        assert window.ground_button.accessibleName() == "Ground message in local evidence"
        assert window.send_button.accessibleName() == "Send message"
        assert "background: transparent" in window.send_button.styleSheet()
        assert "border: 0" in window.send_button.styleSheet()
        assert controller._nav_buttons[0].isVisible()
        assert controller._nav_buttons[6].isVisible()
        composer = window.prompt_input.parentWidget()
        assert composer is not None
        assert composer.accessibleName() == "Message composer"
        assert composer.maximumWidth() == 1040
        assert composer.width() <= window.width()

        rail = window.findChild(QFrame, "v3Rail")
        assert rail is not None
        assert rail.width() == 72
        assert controller._header.height() == 58
        assert controller._header.hint_label.isHidden()
        assert controller._command_button.text() == "Ctrl K"
        assert controller._command_button.property("compact") is True
        assert controller._command_button.maximumWidth() == 70
        assert all(button.width() == 58 for button in controller._nav_buttons.values())
        assert controller._pallas_button.width() == 58
        assert all(
            label.isHidden()
            for label in window.findChildren(QLabel, "v3MetaLabel")
        )
        assert window.chat_selector.minimumWidth() == 150
        assert window.model_selector.minimumWidth() == 145

        window.resize(1480, 900)
        app.processEvents()
        assert rail.width() == 78
        assert controller._header.height() == 68
        assert controller._header.hint_label.isVisible()
        assert controller._command_button.text() == "Command   Ctrl K"
        assert controller._command_button.property("compact") is False
        assert all(button.width() == 64 for button in controller._nav_buttons.values())
        assert controller._pallas_button.width() == 64
        assert all(
            label.isVisible()
            for label in window.findChildren(QLabel, "v3MetaLabel")
        )
        assert window.chat_selector.minimumWidth() == 190
        assert window.model_selector.minimumWidth() == 170

        window.prompt_input.setEnabled(True)
        window.prompt_input.setFocus(Qt.FocusReason.TabFocusReason)
        app.processEvents()
        assert window.prompt_input.hasFocus()
    finally:
        window.close()
        app.processEvents()
